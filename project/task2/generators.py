"""
Task 2: Generators - Lazy Stream Processing System

This module implements a system for lazy stream processing using Python generators.
It includes data generators, pipeline functions, and aggregators.
"""


from typing import (
    Any,
    Callable,
    Generator,
    Iterable,
    List,
    Dict,
    Union,
    Tuple,
    Iterator,
)
from functools import reduce


def data_generator(
    data_source: Union[List[Any], Generator[Any, None, None], range, Iterable[Any]]
) -> Generator[Any, None, None]:
    """
    Generator for input data generation.

    Args:
        data_source: Source of data (list, generator, or range)

    Yields:
        Data items from the source
    """
    if isinstance(data_source, Generator):
        yield from data_source
    else:
        for item in data_source:
            yield item


class Pipeline:
    """Pipeline for lazy stream processing"""

    def __init__(self, data: Iterable[Any]) -> None:
        """
        Initialize pipeline with data source.

        Args:
            data: Source iterable data
        """
        self.data: Iterable[Any] = data
        self.steps: List[
            Tuple[Callable[..., Any], Tuple[Any, ...], Dict[str, Any]]
        ] = []

    def pipe(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "Pipeline":
        """
        Add a step to the pipeline.

        Args:
            func: Function to apply
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Self for method chaining
        """
        self.steps.append((func, args, kwargs))
        return self

    def __iter__(self) -> Iterator[Any]:
        """
        Apply all steps as we iterate.

        Returns:
            Iterator over processed data
        """
        it: Iterable[Any] = self.data
        for func, args, kwargs in self.steps:
            it = func(*args, it, **kwargs)
        return iter(it)

    def collect(
        self,
        collector: Callable[[Iterable[Any]], Any] = list,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Collects the stream into a collection.

        Args:
            collector: Function or class to collect results (list, set, tuple, dict, etc.)
            *args: Positional arguments for the collector
            **kwargs: Keyword arguments for the collector

        Returns:
            Collected data in the specified format
        """
        return collector(self.__iter__(), *args, **kwargs)


def as_func(
    f: Callable[..., Any], *args: Any, **kwargs: Any
) -> Callable[[Iterable[Any]], Iterator[Any]]:
    """
    Convert a function to work with pipeline.

    Args:
        f: Function to wrap
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Wrapped function that takes an iterable and returns an iterator
    """
    if f in [filter, map, enumerate]:
        return lambda it: f(*args, it, **kwargs)
    elif f == reduce:
        if len(args) >= 2:
            return lambda it: iter([f(args[0], it, *args[1:], **kwargs)])
        else:
            return lambda it: iter([f(*args, it, **kwargs)])
    else:
        return lambda it: f(it, *args, **kwargs)
