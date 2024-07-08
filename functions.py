import numpy as np
import cv2
from skimage.segmentation import slic, mark_boundaries
from scipy.interpolate import splprep, splev
import math
import os
import pydicom
import time


# Define the function to process DICOM files and plot the bounding box with the least white pixels
def process_dicom_files(dicom_folder):

    time_prev = time.process_time()

    dicom_files = read_dicom_folder(dicom_folder)
    print(f"Time Taken - Folder Read: {(time.process_time() - time_prev)}")

    # Define the range of slices to process (4/10 to 6/10)
    start_index = int(len(dicom_files) * (9 / 20))
    end_index = int(len(dicom_files) * (11 / 20))

    min_white_pixels = float('inf')
    best_dicom_data = None

    for dicom_file in dicom_files[start_index:end_index]:
        dicom_data = pydicom.dcmread(dicom_file)
        bounding_boxes, multichannel_image, edge_points = detect_knee_bounding_boxes(dicom_data)

        # Check for similar sized bounding boxes
        if has_similar_sized_boxes(bounding_boxes, tolerance=10):
            for box in bounding_boxes:
                white_pixels = count_white_pixels(multichannel_image, box)
                if white_pixels < min_white_pixels:
                    min_white_pixels = white_pixels
                    best_dicom_data = dicom_data

    return best_dicom_data


# Define the function to check if there are bounding boxes with similar sizes and x-axis length > y-axis length
def has_similar_sized_boxes(bounding_boxes, tolerance=10):
    for i in range(len(bounding_boxes)):
        for j in range(i + 1, len(bounding_boxes)):
            x1, y1, w1, h1 = bounding_boxes[i]
            x2, y2, w2, h2 = bounding_boxes[j]
            if abs(w1 - w2) <= tolerance and abs(h1 - h2) <= tolerance:
                # Check if x-axis length is strictly greater than y-axis length
                if w1 > h1 and w2 > h2:
                    return True
                if w1 > h2 and w2 > h1:
                    return True
    return False


# Define the function to calculate the number of white pixels in a bounding box
def count_white_pixels(image, box):
    x, y, w, h = box
    roi = image[y:y+h, x:x+w]
    return np.sum(roi == 255)


def process_image(dicom_data):
        img = dicom_data.pixel_array.astype(float)
        if 'RescaleSlope' in dicom_data and 'RescaleIntercept' in dicom_data:
            slope = dicom_data.RescaleSlope
            intercept = dicom_data.RescaleIntercept
            img = img * slope + intercept

        img = apply_ct_window(img, [400, 50])
        img = (img - np.min(img)) / (np.max(img) - np.min(img)) * 255
        multichannel_image = np.stack((img,) * 3, axis=-1).astype('uint8')
        return multichannel_image



# Define the function to read DICOM files from a folder and sort them numerically
def read_dicom_folder(folder_path):
    dicom_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dcm'):
                dicom_files.append(os.path.join(root, file))

    # Sort DICOM files numerically
    dicom_files.sort(key=lambda x: int(os.path.basename(x).split('-')[2].split('.')[0]))

    return dicom_files


def find_outliers_with_bspline(points, threshold=1.0):
    """
    Identify outliers in a set of points representing a complex curved shape using B-spline fitting.

    Parameters:
    points (list of tuples): List of (x, y) points.
    threshold (float): Distance threshold to identify outliers.

    Returns:
    list of tuples: List of outlier points.
    list of tuples: List of fitted points on the B-spline curve.
    """
    # Separate x and y coordinates
    x = [p[0] for p in points]
    y = [p[1] for p in points]

    # Fit a B-spline to the data
    tck, u = splprep([x, y], s=2)

    # Evaluate the B-spline to get the fitted points
    fitted_points_x, fitted_points_y = splev(u, tck)
    fitted_points = list(zip(fitted_points_x, fitted_points_y))

    # Calculate the residuals (distances from the points to the fitted curve)
    residuals = [math.sqrt((x[i] - fitted_points_x[i])**2 + (y[i] - fitted_points_y[i])**2) for i in range(len(points))]

    print(residuals)

    # Identify outliers as points with large residuals
    outliers = [points[i] for i, r in enumerate(residuals) if r > threshold]
    filtered_points = [points[i] for i, r in enumerate(residuals) if r <= threshold]

    return outliers, filtered_points


def ls_circle(xx, yy):
    asize = np.size(xx) # number of coordinate points given, at least 30 minimum for the Cobb's Method
    J = np.zeros((asize, 3)) # Jacobian matrix
    K = np.zeros(asize)

    for ix in range(0, asize):
        x = xx[ix]
        y = yy[ix]

        J[ix, 0] = x*x + y*y
        J[ix, 1] = x
        J[ix, 2] = y
        K[ix] = 1.0

    K = K.transpose()
    JT = J.transpose()
    JTJ = np.dot(JT, J)
    InvJTJ = np.linalg.inv(JTJ)

    # Determining the coefficients
    ABC = np.dot(InvJTJ, np.dot(JT, K))
    A = ABC[0]
    B = ABC[1]
    C = ABC[2]

    xofs = -B / (2 * A) # x-coordinate of the center
    yofs = -C / (2 * A) # y-coordinate of the center
    R = np.sqrt(4 * A + B*B + C*C) / (2 * A) # radius of the best fit circle
    if R < 0.0: # can't have a negative radius
        R = -R

    return xofs, yofs, R


def apply_ct_window(img, window):
    # window = (window width, window level)
    R = (img - window[1] + 0.5 * window[0]) / window[0]
    R[R < 0] = 0
    R[R > 1] = 1
    return R


def detect_knee_bounding_boxes(dicom_data):
    dicom_image = dicom_data.pixel_array

    if 'RescaleSlope' in dicom_data and 'RescaleIntercept' in dicom_data:
        slope = dicom_data.RescaleSlope
        intercept = dicom_data.RescaleIntercept
        hu_image = dicom_image * slope + intercept
    else:
        hu_image = dicom_image

    multichannel_image = np.stack((hu_image,) * 3, axis=-1)
    segments = slic(multichannel_image, n_segments=100, compactness=10)
    blurred_image = cv2.GaussianBlur(hu_image, (3, 3), 0)
    laplacian = cv2.Laplacian(blurred_image, cv2.CV_64F)
    sharpened_image = np.uint8(np.clip(blurred_image + laplacian, 0, 255))
    superpixel_edges = mark_boundaries(sharpened_image, segments, color=(1, 0, 0))
    _, binary_image = cv2.threshold(blurred_image, 160, 255, cv2.THRESH_BINARY)
    sobel_x = cv2.Sobel(binary_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(binary_image, cv2.CV_64F, 0, 1, ksize=3)
    sobel_edge = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    sobel_edge_resized = cv2.resize(sobel_edge.astype(np.uint8), (dicom_image.shape[1], dicom_image.shape[0]))

    # Find contours representing edges
    contours, _ = cv2.findContours(sobel_edge_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract coordinates of contours and store them with corresponding bounding boxes
    edge_points = []
    bounding_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 70 and h > 70:
            bounding_boxes.append((x, y, w, h))
        for point in contour:
            edge_points.append(tuple(point[0]))

    # Sort bounding boxes by x-coordinate
    bounding_boxes.sort(key=lambda x: x[0])

    return bounding_boxes, multichannel_image, edge_points
