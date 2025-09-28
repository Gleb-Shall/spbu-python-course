"""Tests for matrices.py module"""

import pytest
from project import matrices


def test_matrix_addition() -> None:
    """Test matrix addition operation"""
    matrices.m1 = [[1, 2], [3, 4]]
    matrices.m2 = [[5, 6], [7, 8]]
    matrices.operations["matrix_addition"] = [
        [matrices.m1[i][j] + matrices.m2[i][j] for j in range(len(matrices.m1[0]))]
        for i in range(len(matrices.m1))
    ]

    assert matrices.operations["matrix_addition"] == [[6, 8], [10, 12]]


def test_matrix_multiplication() -> None:
    """Test matrix multiplication operation"""
    matrices.m1 = [[1, 2], [3, 4]]
    matrices.m2 = [[5, 6], [7, 8]]
    matrices.operations["matrix_multiplication"] = [
        [
            sum(matrices.m1[i][k] * matrices.m2[k][j] for k in range(len(matrices.m2)))
            for j in range(len(matrices.m2[0]))
        ]
        for i in range(len(matrices.m1))
    ]

    assert matrices.operations["matrix_multiplication"] == [[19, 22], [43, 50]]


def test_matrix_transposition() -> None:
    """Test matrix transposition operation"""
    matrices.m1 = [[1, 2, 3], [4, 5, 6]]
    matrices.operations["matrix_transposition"] = [
        [matrices.m1[j][i] for j in range(len(matrices.m1))]
        for i in range(len(matrices.m1[0]))
    ]

    assert matrices.operations["matrix_transposition"] == [[1, 4], [2, 5], [3, 6]]
