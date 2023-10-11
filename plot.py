from typing import List
import numpy as np
import stl

from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


def plot_stl(mesh: stl.mesh.Mesh, theta: List[float]):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f'Optimal Orientation for Figure')

    mesh = stl.mesh.Mesh(mesh.data.copy())
    mesh.rotate([1, 0, 0], theta[0])
    mesh.rotate([0, 1, 0], theta[1])
    if len(theta) > 2:
        mesh.rotate([0, 0, 1], theta[2])

    stl_polys = mplot3d.art3d.Poly3DCollection(mesh.vectors)
    stl_polys.set_facecolor('gold')
    stl_polys.set_edgecolor('black')
    ax.add_collection3d(stl_polys)
    scale = mesh.points.ravel()
    ax.auto_scale_xyz(scale, scale, scale)
    plt.show()
