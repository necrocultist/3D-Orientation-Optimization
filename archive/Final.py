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

    def __identify_stable_faces(self, min_face_area):
        face_areas = np.zeros(len(self.mesh_data.vectors))
        for i, face in enumerate(self.mesh_data.vectors):
            v1, v2, v3 = face

            normal = np.cross(v2 - v1, v3 - v1)
            area = 0.5 * np.linalg.norm(normal)
            face_areas[i] = area

        stable_face_indices = np.where(face_areas >= min_face_area)[0]
        return stable_face_indices

    def __find_min_stress_direction_for_face(self, face_index, overhang_threshold):
        orientation_vector = np.array([0, 0, 1])
        min_stress = float('inf')

        for axis in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
            for rotation_angle in [0, 90, 180, 270]:
                temp_mesh = self.mesh_data
                temp_mesh.rotate(theta=np.deg2rad(rotation_angle), axis=axis)

                stress = self.__calculate_stress_for_face(temp_mesh, face_index, overhang_threshold)

                if stress < min_stress:
                    min_stress = stress
                    orientation_vector = axis

        return orientation_vector

    def __calculate_stress_for_face(self, rotated_mesh, face_index, overhang_threshold):
        face_vertices = rotated_mesh.vectors[face_index]
        min_coords = np.min(face_vertices, axis=0)
        overhang_count = 0

        for vertex in face_vertices:
            if vertex[2] > min_coords[2] + np.tan(np.radians(overhang_threshold)) * (vertex[0] - min_coords[0]):
                overhang_count += 1

        return overhang_count / len(face_vertices)

    def __calculate_support_volume_for_orientation(self, rotated_mesh, stable_faces):
        support_volume = 0
        min_z = np.min(rotated_mesh.vectors[:, :, 2])

        for face_index in stable_faces:
            face = rotated_mesh.vectors[face_index]
            min_face_z = np.min(face[:, 2])

            if min_face_z <= min_z:
                support_volume += 1

        return support_volume

    def choose_best_printing_orientation(self, min_face_area, overhang_threshold):
        self.__load_mesh()
        stable_faces = self.__identify_stable_faces(min_face_area)

        best_orientation = None
        min_support_volume = float('inf')

        for face_index in stable_faces:
            orientation_vector = self.__find_min_stress_direction_for_face(face_index, overhang_threshold)

            rotated_mesh = self.mesh_data
            rotated_mesh.rotate(theta=orientation_vector[0], axis=orientation_vector[1])

            support_volume = self.__calculate_support_volume_for_orientation(rotated_mesh, stable_faces)

            if support_volume < min_support_volume:
                min_support_volume = support_volume
                best_orientation = orientation_vector

        modified_mesh = self.mesh_data
        modified_mesh.rotate(best_orientation[0], best_orientation[1])
        return best_orientation

    def rotate_and_save(self, best_orientation, object_name):
        modified_mesh = self.mesh_data
        modified_mesh.rotate(best_orientation[0], best_orientation[1])
        modified_mesh.save(f"Objects/{object_name}.stl")
        self.stl_file = f"Objects/{object_name}.stl"

    def visualize_object(self):
        mesh = o3d.io.read_triangle_mesh(self.stl_file)
        mesh = mesh.compute_vertex_normals()
        o3d.visualization.draw_geometries([mesh], window_name = "3D STL", left=1000, top=200, width=800, height=650)

if __name__ == "__main__":
    object_stl = STLAnalyzer("Objects/d20_fair.stl", threshold_angle_degrees=45)
    min_face_area = 12.5
    overhang_threshold = 45
    best_orientation = object_stl.choose_best_printing_orientation(min_face_area, overhang_threshold)
    object_stl.rotate_and_save(best_orientation, "output")
    object_stl.visualize_object()