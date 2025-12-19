"""
Implementation of Task 3 - Decorators
curry_explicit, uncurry_explicit, cache_results
Functions to curry, uncurry and cache functions
"""

import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, overload


F = TypeVar("F", bound=Callable[..., Any])


def _make_hashable(obj: Any) -> Any:
    """
    Convert unhashable objects to hashable tuples.

    Args:
        obj: Object to make hashable

    Returns:
        Hashable version of the object
    """
    if isinstance(obj, (list, tuple)):
        return tuple(_make_hashable(item) for item in obj)
    elif isinstance(obj, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, set):
        return tuple(sorted(_make_hashable(item) for item in obj))
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # For other types, try to convert to tuple if possible
        try:
            hash(obj)
            return obj
        except TypeError:
            # If still unhashable, convert to string representation
            return str(obj)


def curry_explicit(function: F, arity: int) -> Callable[..., Any]:
    """
    Convert a function to curry it.

    Args:
        function: Function to wrap
        arity: Arity of the function

    Returns:
        Wrapped function that takes an arguments = arity and returns a result of the function
    """

    if arity < 0:
        raise ValueError("Arity cannot be negative")

    @functools.wraps(function)
    def curried(*args: Any) -> Any:
        """
        subfunction to convert a function to curry it.

        Args:
            args: Arguments to pass to the function

        Returns:
            Wrapped function that takes an some arguments < arity
            if arguments == arity returns a result of the function
        """

        if len(args) > arity:
            raise ValueError(f"Too many arguments for curried function")
        elif len(args) == arity:
            return function(*args)
        else:
            get_new_arg = lambda *a: args + a
            new_arg = get_new_arg()
            if len(new_arg) <= 1:
                return curried(*(args + new_arg))
            else:
                raise ValueError("Too many arguments for curried function")

    return curried


def uncurry_explicit(function: F, arity: int) -> Callable[..., Any]:
    """
    Convert a function to uncurry it.

    Args:
        function: Function to wrap
        arity: Arity of the function

    Returns:
        Wrapped function that takes an arguments = arity and returns a result of the function
    """

    if arity < 0:
        raise ValueError("Arity cannot be negative")

    def uncurried(*args: Any) -> Any:
        """
        subfunction to convert a function to uncurry it.

        Args:
            args: Arguments to pass to the function

        Returns:
            Result of the function
        """

        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, got {len(args)}")

        # If arity is 0, call function with no arguments
        if arity == 0:
            return function()

        # For arity > 0, call function with first argument, then continue with remaining args
        result = function(args[0])
        for i in range(1, arity):
            result = result(args[i])
        return result

    return uncurried


@overload
def cache_results(function: F, *, max_size: Optional[int] = None) -> F:
    ...


@overload
def cache_results(*, max_size: Optional[int] = None) -> Callable[[F], F]:
    ...


def cache_results(
    function: Optional[F] = None, *, max_size: Optional[int] = None
) -> Union[F, Callable[[F], F]]:
    """
    Decorator to cache the results of a function.

    Args:
        function: Function to wrap
        max_size: Maximum size of the cache
    """

    if function is None:
        return lambda f: cache_results(f, max_size=max_size)

    cache: Dict[Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]], Any] = {}
    cache_keys_old: List[Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]]] = []

    @functools.wraps(function)
    def cached(*args: Any, **kwargs: Any) -> Any:
        """
        subfunction to cache the results of a function.

        Args:
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function
        """

        key: Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]] = (
            tuple(_make_hashable(arg) for arg in args),
            tuple(sorted((k, _make_hashable(v)) for k, v in kwargs.items())),
        )

        if key in cache:
            return cache[key]
        else:
            result: Any = function(*args, **kwargs)

            if max_size is None:
                return result

            if len(cache_keys_old) == max_size:
                old_key: Tuple[
                    Tuple[Any, ...], Tuple[Tuple[str, Any], ...]
                ] = cache_keys_old.pop(0)
                del cache[old_key]

            cache[key] = result
            cache_keys_old.append(key)
            return cache[key]

    return cached
