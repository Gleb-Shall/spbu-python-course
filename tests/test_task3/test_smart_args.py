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


class TestSmartArgsComplex:
    """Test complex scenarios with smart_args"""

    def test_complex_function_signature(self):
        """Test complex function with all argument types"""

        @smart_args(support_positional=True)
        def complex_func(x, y=5, *args, z=10, **kwargs):
            return x, y, args, z, kwargs

        result = complex_func(1, 2, 3, 4, z=20, a=30, b=40)
        assert result == (1, 2, (3, 4), 20, {"a": 30, "b": 40})

    def test_isolated_with_nested_mutable_structures(self):
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


class TestSmartArgsComplexMixes:
    """Test complex combinations of Evaluated and Isolated in different modes"""

    def test_keyword_only_multiple_evaluated(self):
        """Test keyword-only with multiple Evaluated parameters"""
        counter1 = [0]
        counter2 = [0]

        def get_counter1():
            counter1[0] += 1
            return counter1[0]

        def get_counter2():
            counter2[0] += 1
            return counter2[0]

        @smart_args
        def func(*, x=Evaluated(get_counter1), y=Evaluated(get_counter2), z=10):
            return x, y, z

        result1 = func(z=20)
        assert result1[0] == result1[1]
        assert result1[2] == 20
        assert counter1[0] >= 1
        assert counter2[0] >= 1

        result2 = func(z=30)
        assert result2[0] > result1[0]
        assert result2[1] > result1[1]
        assert result2[2] == 30

    def test_keyword_only_multiple_isolated(self):
        """Test keyword-only with multiple Isolated parameters"""

        @smart_args
        def func(*, list1=Isolated(), list2=Isolated(), x=5):
            list1.append("a")
            list2.append("b")
            return list1, list2, x

        orig1 = [1, 2]
        orig2 = [3, 4]

        result = func(list1=orig1, list2=orig2, x=10)

        assert orig1 == [1, 2]
        assert orig2 == [3, 4]
        assert result == ([1, 2, "a"], [3, 4, "b"], 10)

    def test_keyword_only_complex_mix_evaluated_isolated(self):
        """Test keyword-only with complex mix of Evaluated and Isolated"""
        eval_counter = [0]

        def get_evaluated():
            eval_counter[0] += 1
            return f"eval_{eval_counter[0]}"

        @smart_args
        def func(
            *,
            eval1=Evaluated(get_evaluated),
            isolated1=Isolated(),
            eval2=Evaluated(get_evaluated),
            isolated2=Isolated(),
            normal=10,
        ):
            isolated1.append(eval1)
            isolated2.append(eval2)
            return eval1, isolated1, eval2, isolated2, normal

        orig1 = ["start1"]
        orig2 = ["start2"]

        result1 = func(isolated1=orig1, isolated2=orig2, normal=20)

        assert orig1 == ["start1"]
        assert orig2 == ["start2"]
        assert result1[0].startswith("eval_")
        assert result1[1] == ["start1", result1[0]]
        assert result1[2].startswith("eval_")
        assert result1[3] == ["start2", result1[2]]
        assert result1[4] == 20
        assert result1[0] != result1[2]

        result2 = func(isolated1=orig1, isolated2=orig2, normal=30)
        assert result2[0] != result1[0]
        assert result2[2] != result1[2]

    def test_positional_multiple_evaluated(self):
        """Test positional with multiple Evaluated parameters"""
        counter1 = [0]
        counter2 = [0]

        def get_counter1():
            counter1[0] += 1
            return counter1[0]

        def get_counter2():
            counter2[0] += 1
            return counter2[0]

        @smart_args(support_positional=True)
        def func(x=Evaluated(get_counter1), y=Evaluated(get_counter2), z=10):
            return x, y, z

        result1 = func(z=20)
        assert result1[0] == result1[1]
        assert result1[2] == 20

        result2 = func(z=30)
        assert result2[0] > result1[0]
        assert result2[1] > result1[1]
        assert result2[2] == 30

        result3 = func(100, 200, z=40)
        assert result3 == (100, 200, 40)

    def test_positional_multiple_isolated(self):
        """Test positional with multiple Isolated parameters"""

        @smart_args(support_positional=True)
        def func(list1=Isolated(), list2=Isolated(), x=5):
            list1.append("a")
            list2.append("b")
            return list1, list2, x

        orig1 = [1, 2]
        orig2 = [3, 4]

        result1 = func(orig1, orig2, x=10)
        assert orig1 == [1, 2]
        assert orig2 == [3, 4]
        assert result1 == ([1, 2, "a"], [3, 4, "b"], 10)

        result2 = func(list1=orig1, list2=orig2, x=20)
        assert orig1 == [1, 2]
        assert orig2 == [3, 4]
        assert result2 == ([1, 2, "a"], [3, 4, "b"], 20)

    def test_positional_pos_evaluated_kw_isolated(self):
        """Test positional Evaluated + keyword-only Isolated"""
        eval_counter = [0]

        def get_evaluated():
            eval_counter[0] += 1
            return eval_counter[0]

        @smart_args(support_positional=True)
        def func(x=Evaluated(get_evaluated), *, isolated=Isolated()):
            isolated.append(x)
            return x, isolated

        orig = ["start"]

        result1 = func(isolated=orig)
        assert result1[0] >= 1
        assert result1[1] == ["start", result1[0]]
        assert orig == ["start"]

        result2 = func(isolated=orig)
        assert result2[0] > result1[0]
        assert result2[1] == ["start", result2[0]]
        assert orig == ["start"]

    def test_positional_pos_isolated_kw_evaluated(self):
        """Test positional Isolated + keyword-only Evaluated"""
        eval_counter = [0]

        def get_evaluated():
            eval_counter[0] += 1
            return f"eval_{eval_counter[0]}"

        @smart_args(support_positional=True)
        def func(isolated=Isolated(), *, evaluated=Evaluated(get_evaluated)):
            isolated.append(evaluated)
            return isolated, evaluated

        orig = ["start"]

        result1 = func(orig)
        assert result1[0] == ["start", result1[1]]
        assert result1[1].startswith("eval_")
        assert orig == ["start"]

        result2 = func(orig)
        assert result2[0] == ["start", result2[1]]
        assert result2[1] != result1[1]
        assert orig == ["start"]

    def test_positional_complex_mix_all_types(self):
        """Test positional with complex mix: pos Evaluated, pos Isolated, kw Evaluated, kw Isolated"""
        eval_counter1 = [0]
        eval_counter2 = [0]

        def get_eval1():
            eval_counter1[0] += 1
            return f"pos_eval_{eval_counter1[0]}"

        def get_eval2():
            eval_counter2[0] += 1
            return f"kw_eval_{eval_counter2[0]}"

        @smart_args(support_positional=True)
        def func(
            pos_eval=Evaluated(get_eval1),
            pos_isolated=Isolated(),
            *,
            kw_eval=Evaluated(get_eval2),
            kw_isolated=Isolated(),
        ):
            pos_isolated.append(pos_eval)
            kw_isolated.append(kw_eval)
            return pos_eval, pos_isolated, kw_eval, kw_isolated

        pos_orig = ["pos_start"]
        kw_orig = ["kw_start"]

        result1 = func(pos_isolated=pos_orig, kw_isolated=kw_orig)

        assert pos_orig == ["pos_start"]
        assert kw_orig == ["kw_start"]
        assert result1[0].startswith("pos_eval_")
        assert result1[1] == ["pos_start", result1[0]]
        assert result1[2].startswith("kw_eval_")
        assert result1[3] == ["kw_start", result1[2]]

        result2 = func(pos_isolated=pos_orig, kw_isolated=kw_orig)
        assert result2[0] != result1[0]
        assert result2[2] != result1[2]

    def test_positional_mix_with_args_kwargs(self):
        """Test positional mix with *args and **kwargs"""
        eval_counter = [0]

        def get_evaluated():
            eval_counter[0] += 1
            return eval_counter[0]

        @smart_args(support_positional=True)
        def func(
            x=Evaluated(get_evaluated),
            isolated=Isolated(),
            *args,
            kw_eval=Evaluated(get_evaluated),
            **kwargs,
        ):
            isolated.append(x)
            isolated.extend(args)
            return x, isolated, args, kw_eval, kwargs

        orig = ["start"]

        result1 = func(isolated=orig, kw_eval=100, extra="value")
        result2 = func(isolated=orig, kw_eval=200, extra="value2")
        result3 = func(999, orig, 1, 2, 3, kw_eval=300, extra="value3")

        assert orig == ["start"]
        assert result1[0] >= 1
        assert result1[1] == ["start", result1[0]]
        assert result1[2] == ()
        assert result1[3] == 100
        assert result1[4] == {"extra": "value"}

        assert result2[0] > result1[0]
        assert result2[1] == ["start", result2[0]]
        assert result2[2] == ()
        assert result2[3] == 200
        assert result2[4] == {"extra": "value2"}

        assert result3[0] == 999
        assert result3[1] == ["start", 999, 1, 2, 3]
        assert result3[2] == (1, 2, 3)
        assert result3[3] == 300
        assert result3[4] == {"extra": "value3"}
        assert orig == ["start"]

    def test_keyword_only_all_evaluated(self):
        """Test keyword-only with all parameters using Evaluated"""
        counters = {"a": 0, "b": 0, "c": 0}

        def get_a():
            counters["a"] += 1
            return counters["a"]

        def get_b():
            counters["b"] += 1
            return counters["b"]

        def get_c():
            counters["c"] += 1
            return counters["c"]

        @smart_args
        def func(*, a=Evaluated(get_a), b=Evaluated(get_b), c=Evaluated(get_c)):
            return a, b, c

        result1 = func()
        assert result1[0] == result1[1] == result1[2]
        assert result1[0] >= 1

        result2 = func()
        assert result2[0] > result1[0]
        assert result2[1] > result1[1]
        assert result2[2] > result1[2]

    def test_keyword_only_all_isolated(self):
        """Test keyword-only with all parameters using Isolated"""

        @smart_args
        def func(*, list1=Isolated(), list2=Isolated(), list3=Isolated()):
            list1.append(1)
            list2.append(2)
            list3.append(3)
            return list1, list2, list3

        orig1 = [10]
        orig2 = [20]
        orig3 = [30]

        result = func(list1=orig1, list2=orig2, list3=orig3)

        assert orig1 == [10]
        assert orig2 == [20]
        assert orig3 == [30]
        assert result == ([10, 1], [20, 2], [30, 3])

    def test_positional_all_evaluated(self):
        """Test positional with all parameters using Evaluated"""
        counters = {"x": 0, "y": 0, "z": 0}

        def get_x():
            counters["x"] += 1
            return counters["x"]

        def get_y():
            counters["y"] += 1
            return counters["y"]

        def get_z():
            counters["z"] += 1
            return counters["z"]

        @smart_args(support_positional=True)
        def func(x=Evaluated(get_x), y=Evaluated(get_y), z=Evaluated(get_z)):
            return x, y, z

        result1 = func()
        assert result1[0] == result1[1] == result1[2]
        assert result1[0] >= 1

        result2 = func()
        assert result2[0] > result1[0]
        assert result2[1] > result1[1]
        assert result2[2] > result1[2]

    def test_positional_all_isolated(self):
        """Test positional with all parameters using Isolated"""

        @smart_args(support_positional=True)
        def func(list1=Isolated(), list2=Isolated(), list3=Isolated()):
            list1.append(1)
            list2.append(2)
            list3.append(3)
            return list1, list2, list3

        orig1 = [10]
        orig2 = [20]
        orig3 = [30]

        result1 = func(orig1, orig2, orig3)
        assert orig1 == [10]
        assert orig2 == [20]
        assert orig3 == [30]
        assert result1 == ([10, 1], [20, 2], [30, 3])

        result2 = func(list1=orig1, list2=orig2, list3=orig3)
        assert orig1 == [10]
        assert orig2 == [20]
        assert orig3 == [30]
        assert result2 == ([10, 1], [20, 2], [30, 3])


class TestSmartArgsNestingErrors:
    """Test that nesting Evaluated and Isolated raises errors in all cases"""

    def test_keyword_only_evaluated_contains_isolated(self):
        """Test that Evaluated(lambda: Isolated()) raises error in keyword-only mode"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args
            def func(*, x=Evaluated(lambda: Isolated())):
                return x

    def test_keyword_only_multiple_nested_evaluated_isolated(self):
        """Test that multiple nested Evaluated(Isolated) raise errors"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args
            def func(
                *,
                x=Evaluated(lambda: Isolated()),
                y=Evaluated(lambda: Isolated()),
            ):
                return x, y

    def test_positional_evaluated_contains_isolated(self):
        """Test that Evaluated(lambda: Isolated()) raises error in positional mode"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args(support_positional=True)
            def func(x=Evaluated(lambda: Isolated())):
                return x

    def test_positional_multiple_nested_evaluated_isolated(self):
        """Test that multiple nested Evaluated(Isolated) raise errors in positional mode"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args(support_positional=True)
            def func(
                x=Evaluated(lambda: Isolated()),
                y=Evaluated(lambda: Isolated()),
            ):
                return x, y

    def test_positional_mixed_nested_keyword_only(self):
        """Test nested Evaluated(Isolated) in both positional and keyword-only args"""
        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args(support_positional=True)
            def func(
                x=Evaluated(lambda: Isolated()),
                *,
                y=Evaluated(lambda: Isolated()),
            ):
                return x, y

    def test_keyword_only_evaluated_with_function_returning_isolated(self):
        """Test that Evaluated with function returning Isolated raises error"""

        def get_isolated():
            return Isolated()

        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args
            def func(*, x=Evaluated(get_isolated)):
                return x

    def test_positional_evaluated_with_function_returning_isolated(self):
        """Test that Evaluated with function returning Isolated raises error in positional mode"""

        def get_isolated():
            return Isolated()

        with pytest.raises(
            AssertionError,
            match="Cannot nest Evaluated and Isolated",
        ):

            @smart_args(support_positional=True)
            def func(x=Evaluated(get_isolated)):
                return x
