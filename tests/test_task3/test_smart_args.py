"""
Tests for smart_args decorator implementation
"""
import pytest
import copy
from project.task3.smart_args import smart_args, Evaluated, Isolated


class TestEvaluated:
    """Test Evaluated class functionality"""

    def test_evaluated_basic(self):
        """Test basic Evaluated functionality"""
        counter = [0]

        def get_counter():
            counter[0] += 1
            return counter[0]

        evaluated = Evaluated(get_counter)
        assert evaluated() == 1
        assert evaluated() == 2
        assert evaluated() == 3

    def test_evaluated_with_lambda(self):
        """Test Evaluated with lambda function"""
        evaluated = Evaluated(lambda: [1, 2, 3])
        result1 = evaluated()
        result2 = evaluated()

        assert result1 == [1, 2, 3]
        assert result2 == [1, 2, 3]
        assert result1 is not result2  # Different instances


class TestSmartArgsKeywordOnly:
    """Test smart_args with support_positional=False (keyword-only mode)"""

    def test_keyword_only_basic(self):
        """Test basic keyword-only functionality"""

        @smart_args
        def func(*, x, y=5):
            return x, y

        assert func(x=1) == (1, 5)
        assert func(x=1, y=2) == (1, 2)

    def test_keyword_only_with_evaluated(self):
        """Test keyword-only with Evaluated defaults"""
        counter = [0]

        @smart_args
        def func(*, x, y=Evaluated(lambda: counter[0] + 1)):
            counter[0] += 1
            return x, y

        assert func(x=1) == (1, 1)
        assert func(x=2) == (2, 2)
        assert func(x=3) == (3, 3)

    def test_keyword_only_with_isolated(self):
        """Test keyword-only with Isolated defaults"""

        @smart_args
        def func(*, x, y=Isolated()):
            y.append(1)
            return x, y

        y_test = [1, 2]

        result1 = func(x=1, y=y_test)
        assert y_test == [1, 2]  # y_test should not be modified
        assert result1 == (1, [1, 2, 1])

    def test_keyword_only_positional_error(self):
        """Test that positional arguments raise error in keyword-only mode"""

        @smart_args
        def func(*, x, y=5):
            return x, y

        with pytest.raises(
            TypeError, match="Function func only accepts keyword arguments"
        ):
            func(1, 2)

    def test_keyword_only_isolated_missing(self):
        """Test missing Isolated argument"""

        @smart_args
        def func(*, x, y=Isolated()):
            return x, y

        with pytest.raises(
            TypeError, match="Parameter 'y' with Isolated\\(\\) must be provided"
        ):
            func(x=1)

    def test_keyword_only_mixed_evaluated_isolated_error(self):
        """Test that mixing Evaluated and Isolated raises error"""
        with pytest.raises(
            AssertionError,
            match="Cannot mix Evaluated and Isolated in the same function",
        ):

            @smart_args
            def func(*, x=Evaluated(lambda: 1), y=Isolated()):
                return x, y


class TestSmartArgsPositional:
    """Test smart_args with support_positional=True"""

    def test_positional_basic(self):
        """Test basic positional functionality"""

        @smart_args(support_positional=True)
        def func(x, y=5):
            return x, y

        assert func(1) == (1, 5)
        assert func(1, 2) == (1, 2)
        assert func(x=1, y=2) == (1, 2)

    def test_positional_with_evaluated(self):
        """Test positional with Evaluated defaults"""
        counter = [0]

        @smart_args(support_positional=True)
        def func(x, y=Evaluated(lambda: counter[0] + 1)):
            counter[0] += 1
            return x, y

        assert func(1) == (1, 1)
        assert func(2) == (2, 2)
        assert func(x=3) == (3, 3)

    def test_positional_with_isolated(self):
        """Test positional with Isolated defaults"""

        @smart_args(support_positional=True)
        def func(x, y=Isolated()):
            y.append(1)
            return x, y

        y_test = [1, 2]
        result1 = func(1, y_test)
        result2 = func(x=2, y=y_test)

        assert y_test == [1, 2]  # y_test should not be modified
        assert result1 == (1, [1, 2, 1])
        assert result2 == (2, [1, 2, 1])

    def test_positional_with_varargs(self):
        """Test positional with *args"""

        @smart_args(support_positional=True)
        def func(x, y=5, *args):
            return x, y, args

        assert func(1) == (1, 5, ())
        assert func(1, 2) == (1, 2, ())
        assert func(1, 2, 3, 4) == (1, 2, (3, 4))

    def test_positional_with_kwargs(self):
        """Test positional with **kwargs"""

        @smart_args(support_positional=True)
        def func(x, y=5, **kwargs):
            return x, y, kwargs

        assert func(1) == (1, 5, {})
        assert func(1, 2) == (1, 2, {})
        assert func(1, 2, z=3, a=4) == (1, 2, {"z": 3, "a": 4})

    def test_positional_with_kwonly(self):
        """Test positional with keyword-only arguments"""

        @smart_args(support_positional=True)
        def func(x, y=5, *, z=10):
            return x, y, z

        assert func(1) == (1, 5, 10)
        assert func(1, 2) == (1, 2, 10)
        assert func(1, 2, z=3) == (1, 2, 3)
        assert func(x=1, y=2, z=3) == (1, 2, 3)

    def test_positional_mixed_evaluated_isolated_error(self):
        """Test that mixing Evaluated and Isolated raises error in positional mode"""
        with pytest.raises(
            AssertionError,
            match="Cannot mix Evaluated and Isolated in the same function",
        ):

            @smart_args(support_positional=True)
            def func(x=Evaluated(lambda: 1), y=Isolated()):
                return x, y


class TestSmartArgsComplex:
    """Test complex scenarios with smart_args"""

    def test_complex_function_signature(self):
        """Test complex function with all argument types"""

        @smart_args(support_positional=True)
        def complex_func(x, y=5, *args, z=10, **kwargs):
            return x, y, args, z, kwargs

        result = complex_func(1, 2, 3, 4, z=20, a=30, b=40)
        assert result == (1, 2, (3, 4), 20, {"a": 30, "b": 40})
