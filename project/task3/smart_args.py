import copy
import inspect
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Set,
    TypeVar,
    Union,
    Optional,
    overload,
)

F = TypeVar("F", bound=Callable[..., Any])


class Evaluated:
    """Class for deferred evaluation of default values"""

    def __init__(self, func: Callable[[], Any]) -> None:
        self.func = func

    def __call__(self) -> Any:
        return self.func()


class Isolated:
    """Class for isolating mutable objects"""

    pass


@overload
def smart_args(func: F, *, support_positional: bool = False) -> F:
    ...


@overload
def smart_args(*, support_positional: bool = False) -> Callable[[F], F]:
    ...


def smart_args(
    func: Optional[F] = None, *, support_positional: bool = False
) -> Union[F, Callable[[F], F]]:
    def decorator(f: F) -> F:
        argspec = inspect.getfullargspec(f)

        # Validations for support_positional=False
        if not support_positional:
            if argspec.args:
                raise AssertionError(
                    f"Positional arguments {argspec.args} must be keyword-only"
                )
            if argspec.varargs:
                raise AssertionError(
                    f"Variable arguments (*{argspec.varargs}) not allowed"
                )

        # Find special parameters (for both modes)
        evaluated_params: Set[str] = set()
        isolated_params: Set[str] = set()

        # Check positional arguments with defaults
        if argspec.defaults:
            num_defaults: int = len(argspec.defaults)
            start_idx: int = len(argspec.args) - num_defaults
            for i, default_value in enumerate(argspec.defaults):
                param_name: str = argspec.args[start_idx + i]
                if isinstance(default_value, Evaluated):
                    evaluated_params.add(param_name)
                elif isinstance(default_value, Isolated):
                    isolated_params.add(param_name)

        # Check keyword-only arguments
        for param_name in argspec.kwonlyargs:
            kwonly_default_value: Any = (
                argspec.kwonlydefaults.get(param_name, inspect.Parameter.empty)
                if argspec.kwonlydefaults
                else inspect.Parameter.empty
            )
            if isinstance(kwonly_default_value, Evaluated):
                evaluated_params.add(param_name)
            elif isinstance(kwonly_default_value, Isolated):
                isolated_params.add(param_name)

        # Essential validation: no nesting (for both modes)
        # Check for nesting: Isolated(Evaluated(...)) or Evaluated(Isolated(...))
        def check_nesting(value):
            """Check if value contains nested Evaluated/Isolated"""
            if isinstance(value, Evaluated):
                # Check if Evaluated contains Isolated
                if hasattr(value, "func") and isinstance(value.func(), Isolated):
                    return True
            elif isinstance(value, Isolated):
                # Check if Isolated contains Evaluated (though this is unlikely)
                # Isolated is just a marker, so this check is mainly for completeness
                pass
            return False

        # Check all default values for nesting
        all_defaults = []
        if argspec.defaults:
            all_defaults.extend(argspec.defaults)
        if argspec.kwonlydefaults:
            all_defaults.extend(argspec.kwonlydefaults.values())

        for default_value in all_defaults:
            if check_nesting(default_value):
                raise AssertionError(
                    "Cannot nest Evaluated and Isolated (e.g., Isolated(Evaluated(...)))"
                )

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not support_positional:
                # Mode 1: Only keyword arguments
                if args:
                    raise TypeError(
                        f"Function {f.__name__} only accepts keyword arguments"
                    )

                # Process keyword-only arguments
                processed_kwargs: Dict[str, Any] = {}
                for key, value in kwargs.items():
                    processed_kwargs[key] = (
                        copy.deepcopy(value) if key in isolated_params else value
                    )

                # Apply defaults for keyword-only arguments
                for param_name in argspec.kwonlyargs:
                    if param_name not in processed_kwargs:
                        processed_default_value: Any = (
                            argspec.kwonlydefaults.get(
                                param_name, inspect.Parameter.empty
                            )
                            if argspec.kwonlydefaults
                            else inspect.Parameter.empty
                        )
                        if isinstance(processed_default_value, Evaluated):
                            processed_kwargs[param_name] = processed_default_value()
                        elif isinstance(processed_default_value, Isolated):
                            raise TypeError(
                                f"Parameter '{param_name}' with Isolated() must be provided"
                            )
                        elif processed_default_value is not inspect.Parameter.empty:
                            processed_kwargs[param_name] = processed_default_value

                return f(**processed_kwargs)

            else:
                # Mode 2: Support positional arguments
                # Handle *args and **kwargs properly
                positional_args: List[Any] = (
                    list(args[: len(argspec.args)]) if argspec.args else []
                )
                varargs: List[Any] = (
                    list(args[len(argspec.args) :]) if argspec.varargs else []
                )

                # Build call arguments directly
                call_args: List[Any] = []
                call_kwargs: Dict[str, Any] = {}

                # Add positional arguments
                # Add positional arguments
                for i, param_name in enumerate(argspec.args):
                    if param_name in kwargs:
                        # Argument was passed as keyword argument
                        kwarg_value: Any = kwargs[param_name]
                        call_args.append(
                            copy.deepcopy(kwarg_value)
                            if param_name in isolated_params
                            else kwarg_value
                        )
                    elif i < len(positional_args):
                        # Argument was passed as positional argument
                        pos_value: Any = positional_args[i]
                        call_args.append(
                            copy.deepcopy(pos_value)
                            if param_name in isolated_params
                            else pos_value
                        )
                    else:
                        # Apply default value
                        if argspec.defaults:
                            num_defaults: int = len(argspec.defaults)
                            start_idx: int = len(argspec.args) - num_defaults
                            if i >= start_idx:
                                pos_default_value: Any = argspec.defaults[i - start_idx]
                                if isinstance(pos_default_value, Evaluated):
                                    call_args.append(pos_default_value())
                                elif isinstance(pos_default_value, Isolated):
                                    raise TypeError(
                                        f"Parameter '{param_name}' with Isolated() must be provided"
                                    )
                                else:
                                    call_args.append(pos_default_value)
                            else:
                                raise TypeError(f"Parameter '{param_name}' is required")
                        else:
                            raise TypeError(f"Parameter '{param_name}' is required")

                # Add *args
                if argspec.varargs and varargs:
                    call_args.extend(varargs)

                # Add keyword-only arguments
                for param_name in argspec.kwonlyargs:
                    if param_name in kwargs:
                        # Argument was passed
                        kwonly_value: Any = kwargs[param_name]
                        call_kwargs[param_name] = (
                            copy.deepcopy(kwonly_value)
                            if param_name in isolated_params
                            else kwonly_value
                        )
                    else:
                        # Apply default value
                        kwonly_default_value: Any = (
                            argspec.kwonlydefaults.get(
                                param_name, inspect.Parameter.empty
                            )
                            if argspec.kwonlydefaults
                            else inspect.Parameter.empty
                        )
                        if isinstance(kwonly_default_value, Evaluated):
                            call_kwargs[param_name] = kwonly_default_value()
                        elif isinstance(kwonly_default_value, Isolated):
                            raise TypeError(
                                f"Parameter '{param_name}' with Isolated() must be provided"
                            )
                        elif kwonly_default_value is not inspect.Parameter.empty:
                            call_kwargs[param_name] = kwonly_default_value
                        else:
                            raise TypeError(f"Parameter '{param_name}' is required")

                # Add **kwargs
                if argspec.varkw:
                    # Find remaining keyword arguments (exclude already processed positional args)
                    used_kwargs: Set[str] = set(argspec.kwonlyargs) | set(argspec.args)
                    remaining_kwargs: Dict[str, Any] = {
                        k: v for k, v in kwargs.items() if k not in used_kwargs
                    }
                    if remaining_kwargs:
                        call_kwargs.update(remaining_kwargs)

            return f(*call_args, **call_kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator(func) if func else decorator


def tests():
    def test1():
        call_count = 0

        def create_value():
            nonlocal call_count
            call_count += 1
            return f"evaluated_{call_count}"

        @smart_args(support_positional=True)
        def test_evaluated(value=Evaluated(create_value)):
            return value

        print(call_count)
        result1 = test_evaluated()
        print(call_count)
        result2 = test_evaluated()
        print(call_count)
        result3 = test_evaluated()
        print(call_count)

    def test2():
        call_count = 0

        def create_value():
            nonlocal call_count
            call_count += 1
            return f"evaluated_{call_count}"

        @smart_args(support_positional=True)
        def test_evaluated(value=Evaluated(create_value)):
            return value

        print(call_count)
        result1 = test_evaluated()
        print(call_count)
        result2 = test_evaluated()
        print(call_count)
        result3 = test_evaluated()
        print(call_count)

    test1()
    test2()


tests()
