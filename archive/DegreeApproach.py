from stl import mesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

class STLAnalyzer:
    def __init__(self, stl_file, threshold_angle_degrees):
        self.stl_file = stl_file
        self.threshold_angle_rad = np.radians(threshold_angle_degrees)

    def __load_mesh(self):
        self.mesh_data = mesh.Mesh.from_file(self.stl_file)
        self.vertices = self.mesh_data.vectors

    def __calculate_angles(self):
        self.faces_requiring_support = []

        for i, facet in enumerate(self.vertices):
            v1, v2, v3 = facet

            # Calculate the normal vector of the face
            normal = np.cross(v2 - v1, v3 - v1)
            normal_len = np.linalg.norm(normal)
            normal /= normal_len

            # Calculate the angle between the face normal and the Z-axis
            angle_rad = np.arccos(np.dot(normal, [0, 0, 1]))

            if angle_rad > self.threshold_angle_rad and normal_len > 25:
                self.faces_requiring_support.append((i, angle_rad))

    def __find_min_area_face(self):
        if self.faces_requiring_support:
            min_area_face = min(self.faces_requiring_support, key=lambda x: np.linalg.norm(
                np.cross(self.vertices[x[0]][1] - self.vertices[x[0]][0], self.vertices[x[0]][2] - self.vertices[x[0]][0])))
            self.min_area_face = min_area_face


    def __print_optimal_face(self):
        if self.faces_requiring_support:
            min_area_face_index, min_area = self.min_area_face
            print(f"Face index with lowest area requiring support: {round(min_area_face_index, 4)}")
            print(f"Area of the face: {round(min_area, 4)}")
        else:
            print("No faces require support.")

    def __visualize_object(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for i, facet in enumerate(self.vertices):
            v1, v2, v3 = facet
            # Plot each face in blue
            ax.plot([v1[0], v2[0], v3[0], v1[0]], [v1[1], v2[1], v3[1], v1[1]], [v1[2], v2[2], v3[2], v1[2]], 'b-')

        if self.faces_requiring_support:
            min_area_face_index, min_area = self.min_area_face

            # Highlight the face that requires support in red
            v1, v2, v3 = self.vertices[min_area_face_index]
            ax.plot([v1[0], v2[0], v3[0], v1[0]], [v1[1], v2[1], v3[1], v1[1]], [v1[2], v2[2], v3[2], v1[2]], 'r-')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.title("3D Object with Highlighted Support Face")

        self.__print_optimal_face()
        plt.show()

    def execute(self):
        self.__load_mesh()
        self.__calculate_angles()
        self.__find_min_area_face()
        self.__visualize_object()

if __name__ == "__main__":
    object_stl = STLAnalyzer("examples/bullet.stl", threshold_angle_degrees=45)
    object_stl.execute()
