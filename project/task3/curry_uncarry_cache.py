"""
Implementation of Task 3 - Decorators
curry_explicit, uncurry_explicit, cache_results
Functions to curry, uncurry and cache functions
"""


import functools


def curry_explicit(function, arity):
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
    def curried(*args):
        """
        subfunction to convert a function to curry it.

        Args:
            args: Arguments to pass to the function

        Returns:
            Wrapped function that takes an some arguments < arity
            if arguments == arity returns a result of the function
        """

        if len(args) > arity:
            raise TypeError(
                f"Too many arguments: expected at most {arity}, got {len(args)}"
            )
        elif len(args) == arity:
            return function(*args)
        else:
            return lambda *a: curried(*(args + a))

    return curried


def uncurry_explicit(function, arity):
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

    def uncurried(*args):
        """
        subfunction to convert a function to uncurry it.

        Args:
            args: Arguments to pass to the function

        Returns:
            Result of the function
        """

        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, got {len(args)}")
        return function(*args)

    return uncurried


def cache_results(function=None, *, max_size=None):
    """
    Decorator to cache the results of a function.

    Args:
        function: Function to wrap
        max_size: Maximum size of the cache
    """

    if function is None:
        return lambda function: cache_results(function, max_size=max_size)

    cache = {}
    cache_keys_old = []

    @functools.wraps(function)
    def cached(*args, **kwargs):
        """
        subfunction to cache the results of a function.

        Args:
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function
        """

        key = (args, tuple(sorted(kwargs.items())))

        if key in cache:
            return cache[key]
        else:
            result = function(*args, **kwargs)

            if max_size is None:
                return result

            if len(cache_keys_old) == max_size:
                old_key = cache_keys_old.pop(0)
                del cache[old_key]

            cache[key] = result
            cache_keys_old.append(key)
            return cache[key]

    return cached
