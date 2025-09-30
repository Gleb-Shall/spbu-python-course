"""
Tests for Pipeline class using pytest.mark.parametrize
"""

import pytest
from project.task2.generators import *


class TestPipelineWithAsFuncChaining:
    """Tests for chaining with as_func"""

    @pytest.mark.parametrize(
        "input_data,operations,expected",
        [
            (
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [
                    (filter, (lambda x: x % 2 == 0,)),
                    (map, (lambda x: x**2,)),
                    (filter, (lambda x: x > 10,)),
                ],
                [16, 36, 64, 100],
            ),
            (
                ["hello", "world", "python", "test"],
                [
                    (filter, (lambda x: len(x) > 4,)),
                    (map, (str.upper,)),
                ],
                ["HELLO", "WORLD", "PYTHON"],
            ),
        ],
    )
    def test_pipeline_as_func_chaining(self, input_data, operations, expected):
        """Test Pipeline with as_func chaining"""
        pipeline = Pipeline(data_generator(input_data))
        for func, args in operations:
            pipeline = pipeline.pipe(as_func(func, *args))
        result = pipeline.collect(list)
        assert result == expected


class TestPipelineCollectors:
    """Tests for different collectors"""

    @pytest.mark.parametrize(
        "input_data,collector,expected",
        [
            ([1, 2, 3, 4, 5], list, [1, 2, 3, 4, 5]),
            ([1, 2, 3, 4, 5], set, {1, 2, 3, 4, 5}),
            ([1, 2, 3, 4, 5], tuple, (1, 2, 3, 4, 5)),
            (["a", "b", "c"], list, ["a", "b", "c"]),
            ([(1, 2), (3, 4), (5, 6)], dict, {1: 2, 3: 4, 5: 6}),
        ],
    )
    def test_pipeline_collectors(self, input_data, collector, expected):
        """Test Pipeline with different collectors"""
        result = Pipeline(data_generator(input_data)).collect(collector)
        assert result == expected
