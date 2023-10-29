import numpy as np
import sys
from operations import build, rotate_and_calculate_time, load_stl
from plot import plot_stl

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Usage: python main.py <stl file>")
        sys.exit(1)
    stl_name = sys.argv[1]
    mesh = load_stl(stl_name)
    obj_fun = build(mesh)

    theta, rotate_time, obj_fun = rotate_and_calculate_time(obj_fun)

    print(
        f'Optimal rotation for {stl_name} is {np.round(theta, decimals=3)} '
        f'with value {np.round(obj_fun, decimals=3)} in '
        f'{np.round(rotate_time, decimals=3)} seconds')

    plot_stl(mesh, theta)
    sys.exit(0)
