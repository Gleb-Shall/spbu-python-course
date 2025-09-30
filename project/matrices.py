"""
Module for matrix operations
covers the following operations:
- matrix addition
- matrix multiplication
- matrix transposition
"""

from typing import List, Union, Generator

# Collection of matrix pairs for dynamic computation
mas_matrices: List[List[List[List[Union[int, float]]]]] = []

# Matrices for calculations
m1: List[List[Union[int, float]]] = [[1, 2], [3, 4]]
m2: List[List[Union[int, float]]] = [[5, 6], [7, 8]]

# Create generators for each operation
addition: Generator[List[List[Union[int, float]]], None, None] = (
    [[m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]
    for m1, m2 in mas_matrices
)
multiplication: Generator[List[List[Union[int, float]]], None, None] = (
    [
        [sum(m1[i][k] * m2[k][j] for k in range(len(m2))) for j in range(len(m2[0]))]
        for i in range(len(m1))
    ]
    for m1, m2 in mas_matrices
)
transposition: Generator[List[List[Union[int, float]]], None, None] = (
    [[m1[j][i] for j in range(len(m1))] for i in range(len(m1[0]))]
    for m1, m2 in mas_matrices
)
