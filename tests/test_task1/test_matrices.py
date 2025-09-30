"""Tests for matrices.py module"""

import pytest
from project.task1 import matrices


def test_matrix_addition() -> None:
    """Test matrix addition operation"""
    matrices.mas_matrices.append([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    result = next(matrices.addition)
    assert result == [[6, 8], [10, 12]]
    matrices.mas_matrices.pop(-1)


def test_matrix_multiplication() -> None:
    """Test matrix multiplication operation"""
    matrices.mas_matrices.append([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    result = next(matrices.multiplication)
    assert result == [[19, 22], [43, 50]]
    matrices.mas_matrices.pop(-1)


def test_matrix_transposition() -> None:
    """Test matrix transposition operation"""
    matrices.mas_matrices.append(
        [[[1, 2, 3], [4, 5, 6]], [[0]]]
    )  # Transposition is performed for the first matrix in the list of two
    result = next(matrices.transposition)
    assert result == [[1, 4], [2, 5], [3, 6]]
    matrices.mas_matrices.pop(-1)
