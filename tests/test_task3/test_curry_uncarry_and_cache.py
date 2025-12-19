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

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            curried(1, 2)

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
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

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            f2(123)(456, 562)

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            f2(123, 456)(562)

    def test_max_function(self):
        """Test with max function"""
        f2 = curry_explicit(max, 3)
        assert f2(123)(456)(562) == 562

        g2 = uncurry_explicit(f2, 3)

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            f2(123, 456)

        with pytest.raises(TypeError, match="Expected 3 arguments, got 4"):
            g2(123, 456, 562, 678)

    def test_print_function(self):
        """Test with print function"""
        f2 = curry_explicit(print, 3)
        assert f2(123)(56)(562) == None

        g2 = uncurry_explicit(f2, 3)

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            f2(123, 56)(562)

        with pytest.raises(TypeError, match="Expected 3 arguments, got 4"):
            g2(123, 56, 562, 678)

    def test_map_function(self):
        """Test with map function"""
        f2 = curry_explicit(map, 2)
        assert list(f2(lambda x: x * 2)([1, 2, 3])) == [2, 4, 6]


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
            uncurried(1, 2, 3)

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

    def test_max_function(self):
        """Test with max function"""

        f2 = curry_explicit(max, 3)
        g2 = uncurry_explicit(f2, 3)
        assert g2(123, 456, 562) == 562

    def test_print_function(self):
        """Test with print function"""

        f2 = curry_explicit(print, 3)
        g2 = uncurry_explicit(f2, 3)
        assert g2(123, 56, 562) == None

    def test_map_function(self):
        """Test with map function"""
        f2 = curry_explicit(map, 2)
        assert list(f2(lambda x: x * 2)([1, 2, 3])) == [2, 4, 6]

        g2 = uncurry_explicit(f2, 2)
        assert list(g2(lambda x: x * 2, [1, 2, 3])) == [2, 4, 6]


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
        assert call_count == 2

    def test_caching_with_max_size(self):
        """Test caching with limited size"""
        call_count = 0

        @cache_results(max_size=2)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive_function(1) == 2
        assert call_count == 1

        assert expensive_function(1) == 2
        assert call_count == 1

        assert expensive_function(2) == 4
        assert call_count == 2

        assert expensive_function(3) == 6
        assert call_count == 3

        assert expensive_function(1) == 2
        assert call_count == 4

    def test_positional_arguments(self):
        """Test with positional arguments"""
        call_count = 0

        @cache_results(max_size=3)
        def add(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        assert add(1, 2) == 3
        assert add(1, 2) == 3
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
        assert multiply(2, 3, z=4) == 24
        assert call_count == 1

    def test_caching_works_with_unhashable_arguments(self):
        """Test that caching now works with unhashable arguments (list, dict, set)"""
        call_count = 0

        @cache_results(max_size=5)
        def process_data(data):
            nonlocal call_count
            call_count += 1
            if isinstance(data, list):
                return [x * 2 for x in data]
            elif isinstance(data, dict):
                return {k: v * 2 for k, v in data.items()}
            elif isinstance(data, set):
                return {x * 2 for x in data}
            return data

        list_data = [1, 2, 3]
        result1 = process_data(list_data)
        result2 = process_data(list_data)
        assert result1 == [2, 4, 6]
        assert result2 == [2, 4, 6]
        assert result1 is result2
        assert call_count == 1

        dict_data = {"a": 1, "b": 2}
        result3 = process_data(dict_data)
        result4 = process_data(dict_data)
        assert result3 == {"a": 2, "b": 4}
        assert result4 == {"a": 2, "b": 4}
        assert result3 is result4
        assert call_count == 2

        set_data = {1, 2, 3}
        result5 = process_data(set_data)
        result6 = process_data(set_data)
        assert result5 == [2, 4, 6]
        assert result6 == [2, 4, 6]
        assert result5 is result6

    def test_caching_works_with_mixed_hashable_unhashable_arguments(self):
        """Test that caching works when mixing hashable and unhashable arguments"""
        call_count = 0

        @cache_results(max_size=5)
        def mixed_function(x, data, y=10):
            nonlocal call_count
            call_count += 1
            return x + len(data) + y

        result1 = mixed_function(5, [1, 2, 3], y=20)
        result2 = mixed_function(5, [1, 2, 3], y=20)
        assert result1 == 5 + 3 + 20
        assert result2 == 28
        assert result1 is result2
        assert call_count == 1

        result3 = mixed_function(5, {"a": 1, "b": 2}, y=20)
        result4 = mixed_function(5, {"a": 1, "b": 2}, y=20)
        assert result3 == 5 + 2 + 20
        assert result4 == 27
        assert result3 is result4
        assert call_count == 2

        result5 = mixed_function(5, {1, 2, 3, 4}, y=20)
        result6 = mixed_function(5, {1, 2, 3, 4}, y=20)
        assert result5 == 5 + 4 + 20
        assert result6 == 29
        assert result5 is result6
        assert call_count == 3

    def test_caching_works_with_keyword_unhashable_arguments(self):
        """Test that caching works with unhashable keyword arguments"""
        call_count = 0

        @cache_results(max_size=3)
        def keyword_function(x, data=None):
            nonlocal call_count
            call_count += 1
            if data is None:
                data = []
            return x + len(data)

        result1 = keyword_function(5, data=[1, 2, 3])
        result2 = keyword_function(5, data=[1, 2, 3])
        assert result1 == 8
        assert result2 == 8
        assert result1 is result2
        assert call_count == 1

        result3 = keyword_function(5, data={"a": 1, "b": 2})
        result4 = keyword_function(5, data={"a": 1, "b": 2})
        assert result3 == 7
        assert result4 == 7
        assert result3 is result4
        assert call_count == 2

    def test_cache_behavior_after_multiple_iterations(self):
        """Test cache behavior after multiple iterations"""
        call_count = 0

        @cache_results(max_size=3)
        def fibonacci(n):
            nonlocal call_count
            call_count += 1
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        result1 = fibonacci(5)
        assert result1 == 5
        assert call_count == 6

        call_count = 0
        result2 = fibonacci(5)
        assert result2 == 5
        assert call_count == 0

        call_count = 0
        result3 = fibonacci(6)
        assert result3 == 8
        assert call_count == 1

    def test_cache_eviction_after_iterations(self):
        """Test cache eviction behavior after multiple iterations"""
        call_count = 0

        @cache_results(max_size=2)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * x

        result1 = expensive_function(1)
        result2 = expensive_function(2)
        assert call_count == 2

        result3 = expensive_function(1)
        assert result3 == 1
        assert call_count == 2

        result4 = expensive_function(3)
        assert result4 == 9
        assert call_count == 3

        result5 = expensive_function(1)
        assert result5 == 1
        assert call_count == 4

        result6 = expensive_function(2)
        assert result6 == 4
        assert call_count == 5

    def test_cache_behavior_with_iterative_calls(self):
        """Test cache behavior with iterative function calls"""
        call_count = 0

        @cache_results(max_size=5)
        def factorial(n):
            nonlocal call_count
            call_count += 1
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        result1 = factorial(5)
        assert result1 == 120
        assert call_count == 5

        call_count = 0
        result2 = factorial(5)
        assert result2 == 120
        assert call_count == 0

        call_count = 0
        result3 = factorial(6)
        assert result3 == 720
        assert call_count == 1

    def test_cache_behavior_with_nested_iterations(self):
        """Test cache behavior with nested iterative calls"""
        call_count = 0

        @cache_results(max_size=10)
        def power(base, exp):
            nonlocal call_count
            call_count += 1
            if exp == 0:
                return 1
            if exp == 1:
                return base
            return base * power(base, exp - 1)

        result1 = power(2, 5)
        assert result1 == 32
        assert call_count == 5

        call_count = 0
        result2 = power(2, 5)
        assert result2 == 32
        assert call_count == 0

        call_count = 0
        result3 = power(3, 5)
        assert result3 == 243
        assert call_count == 5

        call_count = 0
        result4 = power(2, 6)
        assert result4 == 64
        assert call_count == 1

    def test_cache_behavior_with_mixed_iterations(self):
        """Test cache behavior with mixed iterative and non-iterative calls"""
        call_count = 0

        @cache_results(max_size=5)
        def mixed_function(x, y):
            nonlocal call_count
            call_count += 1
            if x == 0:
                return y
            return mixed_function(x - 1, y) + y

        result1 = mixed_function(3, 2)
        assert result1 == 8
        assert call_count == 4

        call_count = 0
        result2 = mixed_function(3, 2)
        assert result2 == 8
        assert call_count == 0

        call_count = 0
        result3 = mixed_function(3, 3)
        assert result3 == 12
        assert call_count == 4

        call_count = 0
        result4 = mixed_function(2, 2)
        assert result4 == 6
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

        curried = curry_explicit(add_three, 3)

        result1 = curried(1)(2)(3)
        assert result1 == 6
        assert call_count == 1

        result2 = curried(1)(2)(3)
        assert result2 == 6
        assert call_count == 1

        with pytest.raises(ValueError, match="Too many arguments for curried function"):
            curried(1, 2)

        uncurried = uncurry_explicit(curried, 3)
        result3 = uncurried(1, 2, 3)
        assert result3 == 6
        assert call_count == 1
