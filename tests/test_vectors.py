"""Tests for vectors.py module"""

import pytest
from project import vectors


def test_lenght_first_vector() -> None:
    """Test calculation of first vector length"""
    vectors.mas_vectors.append([[2], [3]])
    result = next(vectors.leght_first_vector)
    assert result == 2.0
    vectors.mas_vectors.pop(-1)


def test_lenght_second_vector() -> None:
    """Test calculation of second vector length"""
    vectors.mas_vectors.append([[2], [3]])
    result = next(vectors.leght_second_vector)
    assert result == 3.0
    vectors.mas_vectors.pop(-1)


def test_lenght_result_vector() -> None:
    """Test calculation of resulting vector length"""
    vectors.mas_vectors.append([[3, 4], [0, 0]])
    result = next(vectors.lenght_result_vector)
    assert result == 5
    vectors.mas_vectors.pop(-1)


def test_scalar_product() -> None:
    """Test calculation of scalar product"""
    vectors.mas_vectors.append([[3, 4], [4, 8]])
    result = next(vectors.scalar_product)
    assert result == 44
    vectors.mas_vectors.pop(-1)


def test_angle_between_vectors() -> None:
    """Test calculation of angle between vectors"""
    vectors.mas_vectors.append([[1, 1], [1, 0]])
    result = next(vectors.angle_between_vectors)
    assert (
        int(result) == 45
    )  # Due to machine rounding inaccuracy, need to round using int()
    vectors.mas_vectors.pop(-1)
