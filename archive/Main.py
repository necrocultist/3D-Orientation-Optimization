from stl import mesh
import numpy as np
from AverageNormalApproach import  STLAnalyzer

if __name__ == "__main__":
    object_stl = STLAnalyzer("Objects/d20_fair.stl", threshold_angle_degrees=45)

    object_stl.load_mesh()
    object_stl.calculate_angles()
    object_stl.find_min_area_face()
    object_stl.print_optimal_face()
