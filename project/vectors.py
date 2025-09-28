"""
Module for vector operations
covers the following operations:
- length of first vector
- length of second vector
- length of resulting vector
- scalar product
- angle between vectors
"""

from typing import List, Union, Dict
from math import acos, pi

v1: List[Union[int, float]] = [1]
v2: List[Union[int, float]] = [2]

operations: Dict[str, Union[int, float]] = {
    "leght_first_vector": (sum(vd1**2 for vd1 in v1)) ** 0.5,
    "leght_second_vector": (sum(vd2**2 for vd2 in v2)) ** 0.5,
    "lenght_result_vector": (
        sum(vd_res**2 for vd_res in ([vd1 + vd2 for vd1, vd2 in zip(v1, v2)]))
    )
    ** 0.5,
    "scalar_product": sum(vd1 * vd2 for vd1, vd2 in zip(v1, v2)),
    "angle_between_vectors": acos(
        sum(vd1 * vd2 for vd1, vd2 in zip(v1, v2))
        / ((sum(vd1**2 for vd1 in v1)) ** 0.5 * (sum(vd2**2 for vd2 in v2)) ** 0.5)
    )
    * 180
    / pi,
}

__all__ = ["v1", "v2", "operations"]


if __name__ == "__main__":
    print(f" length of first vector: {operations['leght_first_vector'] }")
    print(f" length of second vector: {operations['leght_second_vector'] }")
    print(f" length of resulting vector: {operations['lenght_result_vector']}")
    print(f" scalar product: {operations['scalar_product']}")
    print(f" angle between vectors: {operations['angle_between_vectors']}")
