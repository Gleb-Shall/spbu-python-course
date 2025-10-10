"""
Implementation of Task 3 - Decorators
curry_explicit, uncurry_explicit, cache_results
Functions to curry, uncurry and cache functions
"""

import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, overload


F = TypeVar("F", bound=Callable[..., Any])


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
            return (
                lambda *a: curried(*(args + a))
                if len(a) <= 1
                else (_ for _ in ()).throw(
                    ValueError("Too many arguments for curried function")
                )
            )

    return (
        lambda *a: curried(*a)
        if len(a) <= 1
        else (_ for _ in ()).throw(
            ValueError("Too many arguments for curried function")
        )
    )


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
            args,
            tuple(sorted(kwargs.items())),
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
