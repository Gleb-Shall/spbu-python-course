"""
Tests for as_func helper function using pytest.mark.parametrize
"""

import pytest
from functools import reduce
from project.task2.generators import as_func


class TestAsFunc:
    """Tests for as_func helper function"""

    @pytest.mark.parametrize(
        "func,args,test_data,expected",
        [
            (map, (lambda x: x * 2,), [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]),
            (map, (str.upper,), ["a", "b", "c"], ["A", "B", "C"]),
            (map, (len,), ["hello", "world", "test"], [5, 5, 4]),
            (filter, (lambda x: x % 2 == 0,), [1, 2, 3, 4, 5], [2, 4]),
            (filter, (lambda x: len(x) > 3,), ["a", "ab", "abc", "abcd"], ["abcd"]),
            (enumerate, (), ["a", "b", "c"], [(0, "a"), (1, "b"), (2, "c")]),
            (zip, ([10, 20, 30],), [1, 2, 3], [(1, 10), (2, 20), (3, 30)]),
            (reduce, (lambda x, y: x + y,), [1, 2, 3, 4, 5], [15]),
            (reduce, (lambda x, y: x * y,), [1, 2, 3, 4, 5], [120]),
            (reduce, (lambda x, y: x + y, 10), [1, 2, 3], [16]),
        ],
    )
    def test_as_func(self, func, args, test_data, expected):
        """Test as_func with map and filter functions"""
        wrapped_func = as_func(func, *args)
        result = list(wrapped_func(test_data))
        assert result == expected
