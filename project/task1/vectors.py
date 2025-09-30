"""
Module for vector operations
covers the following operations:
- length of first vector
- length of second vector
- length of resulting vector
- scalar product
- angle between vectors
"""

from typing import List, Union, Generator
from math import acos, pi

# Collection of vector pairs for dynamic computation
mas_vectors: List[List[List[Union[int, float]]]] = []

# Create generators for each operation that compute values dynamically
leght_first_vector: Generator[Union[int, float], None, None] = (
    (sum(vd1**2 for vd1 in v1)) ** 0.5 for v1, v2 in mas_vectors
)
leght_second_vector: Generator[Union[int, float], None, None] = (
    (sum(vd2**2 for vd2 in v2)) ** 0.5 for v1, v2 in mas_vectors
)
lenght_result_vector: Generator[Union[int, float], None, None] = (
    (sum(vd_res**2 for vd_res in ([vd1 + vd2 for vd1, vd2 in zip(v1, v2)]))) ** 0.5
    for v1, v2 in mas_vectors
)
scalar_product: Generator[Union[int, float], None, None] = (
    sum(vd1 * vd2 for vd1, vd2 in zip(v1, v2)) for v1, v2 in mas_vectors
)
angle_between_vectors: Generator[Union[int, float], None, None] = (
    acos(
        (sum(vd1 * vd2 for vd1, vd2 in zip(v1, v2)))
        / ((sum(vd1**2 for vd1 in v1)) ** 0.5 * (sum(vd2**2 for vd2 in v2)) ** 0.5)
    )
    * 180
    / pi
    for v1, v2 in mas_vectors
)
