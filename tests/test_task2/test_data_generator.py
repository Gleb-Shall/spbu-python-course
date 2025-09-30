"""
Tests for data_generator function using pytest.mark.parametrize
"""

import pytest
from project.task2.generators import data_generator


class TestDataGenerator:
    """Tests for data_generator function"""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            (range(1, 6), [1, 2, 3, 4, 5]),
            ([], []),
            ([42], [42]),
            (["a", "b", "c"], ["a", "b", "c"]),
            ((1, 2, 3, 4, 5), [1, 2, 3, 4, 5]),
        ],
    )
    def test_data_generator_with_iterables(self, input_data, expected):
        """Test data_generator with various iterable inputs"""
        result = list(data_generator(input_data))
        assert result == expected

    def test_data_generator_with_generator(self):
        """Test data_generator with generator input"""

        def gen():
            yield 1
            yield 2
            yield 3

        result = list(data_generator(gen()))
        assert result == [1, 2, 3]
