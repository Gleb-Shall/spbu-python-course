"""
Module for matrix operations
covers the following operations:
- matrix addition
- matrix multiplication
- matrix transposition
"""

from typing import List, Union, Dict

# Matrices for calculations
m1: List[List[Union[int, float]]] = [[1, 2], [3, 4]]
m2: List[List[Union[int, float]]] = [[5, 6], [7, 8]]

# Dictionary with operation results
operations: Dict[str, List[List[Union[int, float]]]] = {
    "matrix_addition": [
        [m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))
    ],
    "matrix_multiplication": [
        [sum(m1[i][k] * m2[k][j] for k in range(len(m2))) for j in range(len(m2[0]))]
        for i in range(len(m1))
    ],
    "matrix_transposition": [
        [m1[j][i] for j in range(len(m1))] for i in range(len(m1[0]))
    ],
}

__all__ = ["m1", "m2", "operations"]


if __name__ == "__main__":
    print(f" matrix 1: {m1}")
    print(f" matrix 2: {m2}")
    print(f" matrix addition: {operations['matrix_addition']}")
    print(f" matrix multiplication: {operations['matrix_multiplication']}")
    print(f" matrix transposition: {operations['matrix_transposition']}")
