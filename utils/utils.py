import cv2
import numpy as np
import torch
import triangle as tr


""" Computer cartesian coordinates based on polar coordinates """
def get_cartesian_coordinates(r, azimuth, polar):
    azimuth = np.radians(azimuth)
    polar = np.radians(polar)

    x = r * np.cos(polar) * np.cos(azimuth)
    y = r * np.sin(polar)
    z = r * np.cos(polar) * np.sin(azimuth)

    return [x, y, z]


""" Compute the displacement in the azimuth direction """
def rotate_azimuth(azimuth, displacement):
    azimuth += displacement
    azimuth = azimuth % 360

    return azimuth


""" Compute the displacement in the polar direction """
def rotate_polar(polar, displacement):
    polar += displacement

    polar_cap = 180. / 2. - 0.0001

    if polar > polar_cap:
        return polar_cap

    if polar < -polar_cap:
        return -polar_cap

    return polar


""" Get the 2D mesh based on the rendered image """
def get_contour_mesh(image):
    new_image = np.array(image)
    gray_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)

    # thresholding for white background
    _, binary = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((10, 10), np.uint8)
    dilated_binary = cv2.dilate(binary, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Simplify contours using cv2.approxPolyDP
    epsilon = 1.0  # Adjust this value to control the degree of simplification
    simplified_contours = [cv2.approxPolyDP(contour, epsilon, True) for contour in contours]

    # Process each contour
    vertices_list = [contour.reshape(-1, 2) for contour in simplified_contours]
    vertices = [tuple(vertex.astype(float)) for contour in vertices_list for vertex in
                contour]  # Ensure vertices are tuples of floats

    # Build the list of edges (segments) that define the polygon
    segments = []
    vertex_offset = 0

    for contour in vertices_list:
        num_vertices = len(contour)
        for i in range(num_vertices):
            # Create a segment between consecutive vertices in the contour
            segments.append((i + vertex_offset, (i + 1) % num_vertices + vertex_offset))
        vertex_offset += num_vertices

    a = dict(vertices=vertices, segments=segments)
    b = tr.triangulate(a, 'pq32.5a60')

    vertices = np.array(b['vertices'])
    faces = b['triangles']

    return vertices, faces


""" Compute the bivariate gaussian with a period of 360 """
def periodic_bivariate_gaussian(x, y, mu_x, mu_y, sigma_x, sigma_y):
    total = 0
    for m in range(-1, 2):
        for n in range(-1, 2):
            exponent = -(((x - mu_x + m * 360) ** 2) / (2 * sigma_x ** 2) +
                         ((y - mu_y + n * 360) ** 2) / (2 * sigma_y ** 2))
            total += np.exp(exponent)
    return total


""" Compute a gaussian function value """
def gaussian(value, mean, variance):
    return torch.exp(-((value - mean) ** 2) / (2 * variance ** 2))


""" Get interpolated displacements based on a set of view-deformations and the actual position of the camera """
def get_interpolated_displacements(x, y, gaussian_data, displacement_data, n, nb_data):
    if n == 0:
        tensor_shape = (nb_data, 3)
        return torch.zeros(tensor_shape, device='cuda')
    else:
        n = n-1
        mu_x, mu_y, sigma_x, sigma_y = gaussian_data[n]
        gaussian_n = periodic_bivariate_gaussian(x, y, mu_x, mu_y, sigma_x, sigma_y)
        d = displacement_data[n]
        interpolated_displacements = get_interpolated_displacements(x, y, gaussian_data, displacement_data, n, nb_data)
        return (gaussian_n * (d + interpolated_displacements)
                + (1 - gaussian_n) * interpolated_displacements)


""" Get interpolated jacobians based on a set of view-deformations and the actual position of the camera """
def get_interpolated_jacobians(x, y, gaussian_data, jacobian_data, n, nb_data):
    if n == 0:
        identities = torch.eye(3, device='cuda').repeat(nb_data, 1, 1)
        return identities
    else:
        n = n-1
        mu_x, mu_y, sigma_x, sigma_y = gaussian_data[n]
        gaussian_n = periodic_bivariate_gaussian(x, y, mu_x, mu_y, sigma_x, sigma_y)
        j = jacobian_data[n]
        interpolated_jacobians = get_interpolated_jacobians(x, y, gaussian_data, jacobian_data, n, nb_data)
        return (gaussian_n * (j @ interpolated_jacobians)
                + (1 - gaussian_n) * interpolated_jacobians)
