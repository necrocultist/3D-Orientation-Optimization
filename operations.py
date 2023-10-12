from typing import Dict, List, Callable, Tuple
import numpy as np
import math
import time
import stl
from stl import mesh
from scipy import optimize
from direct import direct


def load_stl(stl_name: str) -> stl.mesh.Mesh:
    """Load an STL file into a numpy array"""
    return stl.mesh.Mesh.from_file(stl_name)


def rotate(fun: Callable[[List[float]], float]) -> Tuple[List[float], float]:
    """Rotate the function f to find the optimal orientation"""
    res: Tuple[List[float], float] = optimize.minimize(fun, [0, 0], method=direct,
                                                       bounds=np.array([[-math.pi, math.pi], [-math.pi, math.pi]]),
                                                       options=dict(maxfev=1000))
    return (res.x, res.fun)


def rotate_and_calculate_time(fun: float) -> Tuple[List[float], float, float]:
    """Rotate the function and calculate the time it takes to do so"""
    start_time: float = time.time()
    theta, fun = rotate(fun)
    finish_time: float = time.time()
    return (theta, finish_time - start_time, fun)


def compute_products(mesh: stl.mesh.Mesh) -> Dict[str, List[float]]:
    """Compute product values for each pair of mesh vectors"""
    sp: Dict[str, List[float]] = {}
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    product = f'{i + 1}{chr(ord("x") + j)}{k + 1}{chr(ord("x") + l)}'
                    product_rev = f'{k + 1}{chr(ord("x") + l)}{i + 1}{chr(ord("x") + j)}'
                    if i == k or j == l:
                        continue
                    if product_rev in sp:
                        sp[product] = sp[product_rev]
                        continue
                    sp[product] = mesh.vectors[:, i, j] * mesh.vectors[:, k, l]
    sp['sa'] = sp['1y2x'] - sp['1x2y'] + sp['1x3y'] - sp['1y3x'] + sp['2y3x'] - sp['2x3y']
    sp['sb'] = sp['1z2x'] - sp['1x2z'] - sp['1z3x'] + sp['2z3x'] + sp['1x3z'] - sp['2x3z']
    sp['sc'] = sp['1z2y'] - sp['1y2z'] - sp['1z3y'] + sp['2z3y'] + sp['1y3z'] - sp['2y3z']

    return sp


def build(mesh: stl.mesh.Mesh):
    """Build the objective function based on the mesh and computed products"""
    sp: Dict[str, List[float]] = compute_products(mesh)

    def fun(theta: List[float]) -> float:
        """Compute the objective function value for the given rotation"""
        sinx = math.sin(theta[0])
        cosx = math.cos(theta[0])
        siny = math.sin(theta[1])
        cosy = math.cos(theta[1])
        cosxcosy = cosx * cosy
        cosysinx = cosy * sinx

        S: List[float] = sp['sa'] * cosxcosy + sp['sb'] * cosysinx + sp['sc'] * siny

        height: List[float] = mesh.vectors[:, :, 2] * cosxcosy - mesh.vectors[:, :, 1] * cosysinx - mesh.vectors[:, :,
                                                                                                    0] * siny
        height_min: float = np.min(height)

        overhang_bias: List[float] = np.tanh(S) + 1.0
        bottom_bias: List[float] = np.tanh((np.sum(height, axis=1) - 3 * height_min) / 10.0)

        return np.sum(np.abs(S) * overhang_bias * bottom_bias) / 4.0

    return fun
