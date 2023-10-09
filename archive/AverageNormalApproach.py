import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import open3d as o3d
from stl import mesh

class STLAnalyzer:
    def __init__(self, stl_file, threshold_angle_degrees):
        self.stl_file = stl_file
        self.threshold_angle_rad = np.radians(threshold_angle_degrees)

    def __load_mesh(self):
        self.mesh_data = mesh.Mesh.from_file(self.stl_file)
        self.vertices = self.mesh_data.vectors

    def __calculate_average_normal(self):
        # Calculate the average normal of all faces
        average_normal = np.zeros(3)

        for facet in self.vertices:
            v1, v2, v3 = facet

            normal = np.cross(v2 - v1, v3 - v1)
            normal /= np.linalg.norm(normal)

            average_normal += normal

        # Normalize the average normal
        self.average_normal = average_normal / np.linalg.norm(average_normal)

    def __rotate_to_z_axis(self):
        # Calculate the rotation matrix to align the average normal with the Z-axis
        z_axis = np.array([0, 0, 1])
        rotation_matrix = np.eye(3)

        if not np.allclose(self.average_normal, z_axis):
            axis = np.cross(self.average_normal, z_axis)
            angle = np.arccos(np.dot(self.average_normal, z_axis))
            rotation_matrix = self.__rotation_matrix(axis, angle)

        # Apply the rotation to the vertices

        # self.vertices = np.dot(rotation_matrix, self.vertices)
        for i in range(len(self.vertices)):
            self.vertices[i] = np.dot(rotation_matrix, self.vertices[i])

    def __rotation_matrix(self, axis, angle):
        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c
        x, y, z = axis

        rotation_matrix = np.array([
            [t * x * x + c, t * x * y - z * s, t * x * z + y * s],
            [t * x * y + z * s, t * y * y + c, t * y * z - x * s],
            [t * x * z - y * s, t * y * z + x * s, t * z * z + c]
        ])

        return rotation_matrix

    def __visualize_object(self):
        mesh = o3d.io.read_triangle_mesh(self.stl_file)
        mesh = mesh.compute_vertex_normals()
        o3d.visualization.draw_geometries([mesh], window_name = "3D STL", left=1000, top=200, width=800, height=650)

    def __save_as_stl(self):
        num_faces = len(self.vertices)
        # modified_vertices = self.vertices.reshape((num_faces, 3, 3))

        modified_mesh = mesh.Mesh(np.zeros(num_faces, dtype=mesh.Mesh.dtype))
        # modified_mesh.vectors = self.vertices
        modified_mesh = self.mesh_data
        modified_mesh.save("Objects/output.stl")
        self.stl_file = "Objects/output.stl"

    def execute(self):
        self.__load_mesh()
        self.__calculate_average_normal()
        self.__rotate_to_z_axis()
        self.__save_as_stl()
        self.__visualize_object()

if __name__ == "__main__":
    object_stl = STLAnalyzer("Objects/d20_fair.stl", threshold_angle_degrees=45)
    object_stl.execute()
