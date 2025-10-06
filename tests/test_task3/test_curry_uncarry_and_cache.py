"""
Tests for Task 3 - curry_explicit, uncurry_explicit, cache_results
"""


import pytest
from project.task3.curry_uncarry_cache import (
    curry_explicit,
    uncurry_explicit,
    cache_results,
)


class TestCurryExplicit:
    """Tests for curry_explicit function"""

    def test_negative_arity(self):
        """Test with negative arity"""
        with pytest.raises(ValueError):
            curry_explicit(lambda x: x, -1)

    def test_too_many_arguments(self):
        """Test with too many arguments"""
        curried = curry_explicit(lambda x, y: x + y, 2)

        with pytest.raises(TypeError):
            curried(1, 2, 3)

    def test_zero_arity(self):
        """Test with arity 0"""

        def constant():
            return 42

        curried = curry_explicit(constant, 0)
        assert curried() == 42

    def test_single_arity(self):
        """Test with arity 1"""

        def square(x):
            return x * x

        curried = curry_explicit(square, 1)
        assert curried(5) == 25

    def test_string_formatting(self):
        """Test from assignment with string formatting"""
        f2 = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)
        assert f2(123)(456)(562) == "<123,456,562>"


class TestUncurryExplicit:
    """Tests for uncurry_explicit function"""

    def test_negative_arity(self):
        """Test with negative arity"""
        with pytest.raises(ValueError):
            uncurry_explicit(lambda x: x, -1)

    def test_wrong_number_of_arguments(self):
        """Test with wrong number of arguments"""
        curried = curry_explicit(lambda x, y: x + y, 2)
        uncurried = uncurry_explicit(curried, 2)

        with pytest.raises(TypeError):
            uncurried(1, 2, 3)  # Too many arguments

    def test_zero_arity(self):
        """Test with arity 0"""

        def constant():
            return 42

        curried = curry_explicit(constant, 0)
        uncurried = uncurry_explicit(curried, 0)
        assert uncurried() == 42

    def test_single_arity(self):
        """Test with arity 1"""

        def square(x):
            return x * x

        curried = curry_explicit(square, 1)
        uncurried = uncurry_explicit(curried, 1)
        assert uncurried(5) == 25

    def test_string_formatting(self):
        """Test from assignment with string formatting"""
        f2 = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)
        g2 = uncurry_explicit(f2, 3)
        assert g2(123, 456, 562) == "<123,456,562>"


class TestCacheResults:
    """Tests for cache_results decorator"""

    def test_no_caching_when_max_size_none(self):
        """Test without caching when max_size = None"""
        call_count = 0

        @cache_results()
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive_function(5) == 10
        assert expensive_function(5) == 10
        assert call_count == 2  # Function called twice

    def test_caching_with_max_size(self):
        """Test caching with limited size"""
        call_count = 0

        @cache_results(max_size=2)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        assert expensive_function(1) == 2
        assert call_count == 1

        # Second call - from cache
        assert expensive_function(1) == 2
        assert call_count == 1

        # New arguments
        assert expensive_function(2) == 4
        assert call_count == 2

        assert expensive_function(3) == 6
        assert call_count == 3

        # First result should be removed from cache
        assert expensive_function(1) == 2
        assert call_count == 4  # Computed again

    def test_positional_arguments(self):
        """Test with positional arguments"""
        call_count = 0

        @cache_results(max_size=3)
        def add(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        assert add(1, 2) == 3
        assert add(1, 2) == 3  # From cache
        assert call_count == 1

    def test_keyword_arguments(self):
        """Test with keyword arguments"""
        call_count = 0

        @cache_results(max_size=3)
        def multiply(x, y, z=1):
            nonlocal call_count
            call_count += 1
            return x * y * z

        assert multiply(2, 3, z=4) == 24
        assert multiply(2, 3, z=4) == 24  # From cache
        assert call_count == 1

    def test_different_keyword_order(self):
        """Test with different order of keyword arguments"""
        call_count = 0

        @cache_results(max_size=3)
        def test_func(x, y, z):
            nonlocal call_count
            call_count += 1
            return x + y + z

        # Different order of keyword arguments should give same result
        result1 = test_func(1, 2, z=3)
        result2 = test_func(1, y=2, z=3)
        result3 = test_func(x=1, y=2, z=3)

        assert result1 == result2
        assert result2 == result3
        # Different ways of passing arguments create different cache keys
        # This is normal behavior for this implementation
        assert call_count == 3


class TestIntegration:
    """Integration tests"""

    def test_curry_and_cache_together(self):
        """Test currying with caching"""
        call_count = 0

        @cache_results(max_size=2)
        def add_three(x, y, z):
            nonlocal call_count
            call_count += 1
            return x + y + z

        # Curry the cached function
        curried = curry_explicit(add_three, 3)

        # First call
        result1 = curried(1)(2)(3)
        assert result1 == 6
        assert call_count == 1

        # Second call - should use cache
        result2 = curried(1)(2)(3)
        assert result2 == 6
        assert call_count == 1  # Did not increase

        # Uncurry
        uncurried = uncurry_explicit(curried, 3)
        result3 = uncurried(1, 2, 3)
        assert result3 == 6
        assert call_count == 1  # Still from cache
