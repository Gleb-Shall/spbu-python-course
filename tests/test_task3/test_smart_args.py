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
        assert result1 is not result2


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
        assert y_test == [1, 2]
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

    def test_keyword_only_mixed_evaluated_isolated_allowed(self):
        """Test that using Evaluated and Isolated in different parameters is allowed"""

        @smart_args
        def func(*, x=Evaluated(lambda: 1), y=Isolated()):
            return x, y

        result = func(x=1, y=[1, 2, 3])
        assert result == (1, [1, 2, 3])

    def test_keyword_only_nested_evaluated_isolated_error(self):
        """Test that nesting Evaluated and Isolated raises error"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args
            def func(*, x=Evaluated(lambda: Isolated())):
                return x


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

        assert y_test == [1, 2]
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

    def test_positional_mixed_evaluated_isolated_allowed(self):
        """Test that using Evaluated and Isolated in different parameters is allowed in positional mode"""

        @smart_args(support_positional=True)
        def func(x=Evaluated(lambda: 1), y=Isolated()):
            return x, y

        result = func(x=1, y=[1, 2, 3])
        assert result == (1, [1, 2, 3])

    def test_positional_nested_evaluated_isolated_error(self):
        """Test that nesting Evaluated and Isolated raises error in positional mode"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args(support_positional=True)
            def func(x=Evaluated(lambda: Isolated())):
                return x


class TestSmartArgsComplex:
    """Test complex scenarios with smart_args"""

    def test_complex_function_signature(self):
        """Test complex function with all argument types"""

        @smart_args(support_positional=True)
        def complex_func(x, y=5, *args, z=10, **kwargs):
            return x, y, args, z, kwargs

        result = complex_func(1, 2, 3, 4, z=20, a=30, b=40)
        assert result == (1, 2, (3, 4), 20, {"a": 30, "b": 40})


class TestSmartArgsBuiltinFunctions:
    """Test smart_args with built-in Python functions"""

    def test_with_len_function(self):
        """Test smart_args with len function"""

        @smart_args
        def test_len(*, data=Evaluated(lambda: [1, 2, 3, 4, 5])):
            return len(data)

        result = test_len()
        assert result == 5

    def test_with_sorted_function(self):
        """Test smart_args with sorted function"""

        @smart_args
        def test_sorted(*, data=Evaluated(lambda: [3, 1, 4, 1, 5])):
            return sorted(data)

        result = test_sorted()
        assert result == [1, 1, 3, 4, 5]

    def test_with_sum_function(self):
        """Test smart_args with sum function"""

        @smart_args
        def test_sum(*, numbers=Evaluated(lambda: [1, 2, 3, 4, 5])):
            return sum(numbers)

        result = test_sum()
        assert result == 15


class TestSmartArgsUnhashableArgs:
    """Test smart_args with unhashable arguments"""

    def test_with_list_args(self):
        """Test smart_args with list arguments"""

        @smart_args
        def test_list(*, data=Isolated()):
            data.append("modified")
            return data

        original_list = [1, 2, 3]
        result = test_list(data=original_list)

        assert original_list == [1, 2, 3]
        assert result == [1, 2, 3, "modified"]

    def test_with_dict_args(self):
        """Test smart_args with dictionary arguments"""

        @smart_args
        def test_dict(*, data=Isolated()):
            data["new_key"] = "new_value"
            return data

        original_dict = {"key1": "value1", "key2": "value2"}
        result = test_dict(data=original_dict)

        assert original_dict == {"key1": "value1", "key2": "value2"}
        assert result == {"key1": "value1", "key2": "value2", "new_key": "new_value"}

    def test_with_set_args(self):
        """Test smart_args with set arguments"""

        @smart_args
        def test_set(*, data=Isolated()):
            data.add("new_item")
            return data

        original_set = {1, 2, 3}
        result = test_set(data=original_set)

        assert original_set == {1, 2, 3}
        assert result == {1, 2, 3, "new_item"}

    def test_nested_mutable_structures(self):
        """Test smart_args with nested mutable structures"""

        @smart_args
        def test_nested(*, data=Isolated()):
            data["list"][0] = "modified"
            data["dict"]["nested"] = "changed"
            return data

        original_data = {"list": [1, 2, 3], "dict": {"nested": "original"}, "value": 42}
        result = test_nested(data=original_data)

        assert original_data == {
            "list": [1, 2, 3],
            "dict": {"nested": "original"},
            "value": 42,
        }
        assert result == {
            "list": ["modified", 2, 3],
            "dict": {"nested": "changed"},
            "value": 42,
        }


class TestSmartArgsCacheIterations:
    """Test smart_args demonstrating cache behavior after iterations"""

    def test_evaluated_cache_behavior(self):
        """Test that Evaluated creates new instances each time"""
        call_count = 0

        def create_list():
            nonlocal call_count
            call_count += 1
            return call_count

        @smart_args
        def test_evaluated(*, data=Evaluated(create_list)):
            return data

        result1 = test_evaluated()
        result2 = test_evaluated()
        result3 = test_evaluated()

        assert call_count == 4
        assert result1 is not result2
        assert result2 is not result3

    def test_isolated_cache_behavior(self):
        """Test that Isolated creates deep copies"""

        @smart_args
        def test_isolated(*, data=Isolated()):
            data.append(len(data))
            return data

        original = [1, 2, 3]

        result1 = test_isolated(data=original)
        result2 = test_isolated(data=original)
        result3 = test_isolated(data=original)

        assert result1 == [1, 2, 3, 3]
        assert result2 == [1, 2, 3, 3]
        assert result3 == [1, 2, 3, 3]
        assert result1 is not result2
        assert result2 is not result3
        assert original == [1, 2, 3]

    def test_evaluated_not_executed_when_arg_provided(self):
        """Test that Evaluated is not executed when argument is provided"""
        call_count = 0

        def create_value():
            nonlocal call_count
            call_count += 1
            return f"evaluated_{call_count}"

        @smart_args
        def test_evaluated(*, value=Evaluated(create_value)):
            return value

        result1 = test_evaluated()
        assert call_count == 2
        assert result1 == f"evaluated_{call_count}"

        result2 = test_evaluated(value="provided_value")
        assert call_count == 2
        assert result2 == "provided_value"

        result3 = test_evaluated()
        assert call_count == 3
        assert result3 == f"evaluated_{call_count}"

    def test_evaluated_not_executed_positional_when_arg_provided(self):
        """Test that Evaluated is not executed when argument is provided in positional mode"""
        call_count = 0

        def create_value():
            nonlocal call_count
            call_count += 1
            return f"evaluated_{call_count}"

        @smart_args(support_positional=True)
        def test_evaluated(value=Evaluated(create_value)):
            return value

        result1 = test_evaluated()
        assert call_count == 2
        assert result1 == f"evaluated_{call_count}"

        result2 = test_evaluated("provided_value")
        assert call_count == 2
        assert result2 == "provided_value"

        result3 = test_evaluated(value="keyword_value")
        assert call_count == 2
        assert result3 == "keyword_value"

        result4 = test_evaluated()
        assert call_count == 3
        assert result4 == f"evaluated_{call_count}"

    def test_mixed_evaluated_isolated_with_provided_args(self):
        """Test mixed Evaluated and Isolated when some arguments are provided"""
        eval_count = 0
        isolated_count = 0

        def create_evaluated():
            nonlocal eval_count
            eval_count += 1
            return f"eval_{eval_count}"

        @smart_args
        def test_mixed(
            *, evaluated_val=Evaluated(create_evaluated), isolated_data=Isolated()
        ):
            isolated_data.append(f"processed_{evaluated_val}")
            return evaluated_val, isolated_data

        result1 = test_mixed(evaluated_val="provided_eval", isolated_data=["test"])
        assert eval_count == 1
        assert result1 == ("provided_eval", ["test", "processed_provided_eval"])

        result2 = test_mixed(isolated_data=["test2"])
        assert eval_count == 2
        assert result2[0] == f"eval_{eval_count}"
        assert result2[1] == ["test2", f"processed_eval_{eval_count}"]

        result3 = test_mixed(evaluated_val="provided_eval2", isolated_data=["test3"])
        assert eval_count == 2
        assert result3[0] == "provided_eval2"
        assert result3[1][-1] == "processed_provided_eval2"

        result4 = test_mixed(isolated_data=["test4"])
        assert eval_count == 3
        assert result4[0] == f"eval_{eval_count}"
        assert result4[1][-1] == f"processed_eval_{eval_count}"

    def test_evaluated_with_included_function(self):
        @smart_args
        def test_function(*, data=Evaluated(lambda: list(zip([1, 2, 3], [4, 5, 6])))):
            return data

        result = test_function()
        assert result == [(1, 4), (2, 5), (3, 6)]


class TestSmartArgsPositionalBuiltinFunctions:
    """Test smart_args with support_positional=True and built-in Python functions"""

    def test_positional_with_len_function(self):
        """Test smart_args with len function in positional mode"""

        @smart_args(support_positional=True)
        def test_len(data=Evaluated(lambda: [1, 2, 3, 4, 5])):
            return len(data)

        result = test_len()
        assert result == 5

    def test_positional_with_sorted_function(self):
        """Test smart_args with sorted function in positional mode"""

        @smart_args(support_positional=True)
        def test_sorted(data=Evaluated(lambda: [3, 1, 4, 1, 5])):
            return sorted(data)

        result = test_sorted()
        assert result == [1, 1, 3, 4, 5]

    def test_positional_with_sum_function(self):
        """Test smart_args with sum function in positional mode"""

        @smart_args(support_positional=True)
        def test_sum(numbers=Evaluated(lambda: [1, 2, 3, 4, 5])):
            return sum(numbers)

        result = test_sum()
        assert result == 15

    def test_positional_with_max_function(self):
        """Test smart_args with max function in positional mode"""

        @smart_args(support_positional=True)
        def test_max(numbers=Evaluated(lambda: [1, 5, 3, 9, 2])):
            return max(numbers)

        result = test_max()
        assert result == 9

    def test_positional_with_min_function(self):
        """Test smart_args with min function in positional mode"""

        @smart_args(support_positional=True)
        def test_min(numbers=Evaluated(lambda: [5, 1, 3, 9, 2])):
            return min(numbers)

        result = test_min()
        assert result == 1


class TestSmartArgsPositionalUnhashableArgs:
    """Test smart_args with support_positional=True and unhashable arguments"""

    def test_positional_with_list_args(self):
        """Test smart_args with list arguments in positional mode"""

        @smart_args(support_positional=True)
        def test_list(data=Isolated()):
            data.append("modified")
            return data

        original_list = [1, 2, 3]
        result = test_list(original_list)

        assert original_list == [1, 2, 3]
        assert result == [1, 2, 3, "modified"]

    def test_positional_with_dict_args(self):
        """Test smart_args with dictionary arguments in positional mode"""

        @smart_args(support_positional=True)
        def test_dict(data=Isolated()):
            data["new_key"] = "new_value"
            return data

        original_dict = {"key1": "value1", "key2": "value2"}
        result = test_dict(original_dict)

        assert original_dict == {"key1": "value1", "key2": "value2"}
        assert result == {"key1": "value1", "key2": "value2", "new_key": "new_value"}

    def test_positional_with_set_args(self):
        """Test smart_args with set arguments in positional mode"""

        @smart_args(support_positional=True)
        def test_set(data=Isolated()):
            data.add("new_item")
            return data

        original_set = {1, 2, 3}
        result = test_set(original_set)

        assert original_set == {1, 2, 3}
        assert result == {1, 2, 3, "new_item"}

    def test_positional_nested_mutable_structures(self):
        """Test smart_args with nested mutable structures in positional mode"""

        @smart_args(support_positional=True)
        def test_nested(data=Isolated()):
            data["list"][0] = "modified"
            data["dict"]["nested"] = "changed"
            return data

        original_data = {"list": [1, 2, 3], "dict": {"nested": "original"}, "value": 42}
        result = test_nested(original_data)

        assert original_data == {
            "list": [1, 2, 3],
            "dict": {"nested": "original"},
            "value": 42,
        }
        assert result == {
            "list": ["modified", 2, 3],
            "dict": {"nested": "changed"},
            "value": 42,
        }

    def test_positional_mixed_positional_keyword_args(self):
        """Test smart_args with mixed positional and keyword arguments"""

        @smart_args(support_positional=True)
        def test_mixed(pos_list=Isolated(), *, kw_dict=Isolated()):
            pos_list.append("pos_modified")
            kw_dict["kw_key"] = "kw_value"
            return pos_list, kw_dict

        original_list = [1, 2, 3]
        original_dict = {"key1": "value1"}

        result = test_mixed(original_list, kw_dict=original_dict)

        assert original_list == [1, 2, 3]
        assert original_dict == {"key1": "value1"}

        assert result[0] == [1, 2, 3, "pos_modified"]
        assert result[1] == {"key1": "value1", "kw_key": "kw_value"}


class TestSmartArgsPositionalCacheIterations:
    """Test smart_args with support_positional=True demonstrating cache behavior after iterations"""

    def test_positional_evaluated_cache_behavior(self):
        """Test that Evaluated creates new instances each time in positional mode"""
        call_count = 0

        def create_list():
            nonlocal call_count
            call_count += 1
            return [call_count]

        @smart_args(support_positional=True)
        def test_evaluated(data=Evaluated(create_list)):
            return data

        result1 = test_evaluated()
        result2 = test_evaluated()
        result3 = test_evaluated()

        assert call_count == 4
        assert result1 is not result2
        assert result2 is not result3

    def test_positional_isolated_cache_behavior(self):
        """Test that Isolated creates deep copies in positional mode"""

        @smart_args(support_positional=True)
        def test_isolated(data=Isolated()):
            data.append(len(data))
            return data

        original = [1, 2, 3]

        result1 = test_isolated(original)
        result2 = test_isolated(original)
        result3 = test_isolated(original)

        assert result1 == [1, 2, 3, 3]
        assert result2 == [1, 2, 3, 3]
        assert result3 == [1, 2, 3, 3]
        assert result1 is not result2
        assert result2 is not result3
        assert original == [1, 2, 3]

    def test_positional_mixed_evaluated_isolated_iterations(self):
        """Test mixed Evaluated and Isolated behavior over multiple iterations in positional mode"""
        counter = 0

        def get_counter():
            nonlocal counter
            counter += 1
            return counter

        @smart_args(support_positional=True)
        def test_mixed(evaluated_val=Evaluated(get_counter), isolated_data=Isolated()):
            isolated_data.append(evaluated_val)
            return evaluated_val, isolated_data

        results = []
        for i in range(3):
            result = test_mixed(isolated_data=[f"iteration_{i}"])
            results.append(result)

        assert counter == 4

        assert results[0][0] == counter - 2
        assert results[1][0] == counter - 1
        assert results[2][0] == counter

        assert results[0][1] is not results[1][1]
        assert results[1][1] is not results[2][1]

    def test_positional_evaluated_not_executed_when_arg_provided(self):
        """Test that Evaluated is not executed when argument is provided in positional mode"""
        call_count = 0

        def create_value():
            nonlocal call_count
            call_count += 1
            return f"evaluated_{call_count}"

        @smart_args(support_positional=True)
        def test_evaluated(value=Evaluated(create_value)):
            return value

        result1 = test_evaluated()
        assert call_count == 2
        assert result1 == f"evaluated_{call_count}"

        result2 = test_evaluated("provided_value")
        assert call_count == 2
        assert result2 == "provided_value"

        result3 = test_evaluated(value="keyword_value")
        assert call_count == 2
        assert result3 == "keyword_value"

        result4 = test_evaluated()
        assert call_count == 3
        assert result4 == f"evaluated_{call_count}"

    def test_positional_complex_iterations_with_varargs(self):
        """Test complex iterations with *args in positional mode"""
        eval_count = 0

        def create_evaluated():
            nonlocal eval_count
            eval_count += 1
            return f"eval_{eval_count}"

        @smart_args(support_positional=True)
        def test_complex(
            isolated_data=Isolated(), *args, evaluated_val=Evaluated(create_evaluated)
        ):
            isolated_data.append(evaluated_val)
            isolated_data.extend(args)
            return evaluated_val, isolated_data, args

        result1 = test_complex(isolated_data=["start"])
        assert eval_count == 2
        assert result1[0] == f"eval_{eval_count}"
        assert result1[1] == ["start", f"eval_{eval_count}"]
        assert result1[2] == ()

        result2 = test_complex(["start2"], 1, 2, 3)
        assert eval_count == 3
        assert result2[0] == f"eval_{eval_count}"
        assert result2[1] == ["start2", f"eval_{eval_count}", 1, 2, 3]
        assert result2[2] == (1, 2, 3)

        result3 = test_complex(["start3"], 4, 5, evaluated_val="provided")
        assert eval_count == 3
        assert result3[0] == "provided"
        assert result3[1] == ["start3", "provided", 4, 5]
        assert result3[2] == (4, 5)
