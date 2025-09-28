"""Tests for vectors.py module"""


import pytest
from project import vectors
from math import acos, pi


def test_lenght_first_vector() -> None:
    """Test calculation of first vector length"""
    vectors.v1 = [0, 5]
    vectors.operations["leght_first_vector"] = (
        sum(vd1**2 for vd1 in vectors.v1)
    ) ** 0.5
    assert vectors.operations["leght_first_vector"] == 5


def test_lenght_second_vector() -> None:
    """Test calculation of second vector length"""
    vectors.v2[0] = 5
    vectors.operations["leght_second_vector"] = (
        sum(vd2**2 for vd2 in vectors.v2)
    ) ** 0.5
    assert vectors.operations["leght_second_vector"] == 5


def test_lenght_result_vector() -> None:
    """Test calculation of resulting vector length"""
    vectors.v1 = [3, 4]
    vectors.v2 = [2, 8]
    vectors.operations["lenght_result_vector"] = (
        sum(
            vd_res**2
            for vd_res in ([vd1 + vd2 for vd1, vd2 in zip(vectors.v1, vectors.v2)])
        )
    ) ** 0.5
    assert vectors.operations["lenght_result_vector"] == 13


def test_scalar_product() -> None:
    """Test calculation of scalar product"""
    vectors.v1 = [3, 4]
    vectors.v2 = [2, 8]
    vectors.operations["scalar_product"] = sum(
        vd1 * vd2 for vd1, vd2 in zip(vectors.v1, vectors.v2)
    )
    assert vectors.operations["scalar_product"] == 38


def test_angle_between_vectors() -> None:
    """Test calculation of angle between vectors"""
    vectors.v1 = [1, 1]
    vectors.v2 = [1, 0]
    vectors.operations["angle_between_vectors"] = (
        acos(
            sum(vd1 * vd2 for vd1, vd2 in zip(vectors.v1, vectors.v2))
            / (
                (sum(vd1**2 for vd1 in vectors.v1)) ** 0.5
                * (sum(vd2**2 for vd2 in vectors.v2)) ** 0.5
            )
        )
        * 180
        / pi
    )
    assert int(vectors.operations["angle_between_vectors"]) == 45
