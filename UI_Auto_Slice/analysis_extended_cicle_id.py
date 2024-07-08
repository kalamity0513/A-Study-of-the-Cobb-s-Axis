import cv2
import pydicom
import numpy as np
from skimage.segmentation import mark_boundaries, slic

# Function to process DICOM image, enhance boundaries, and display using OpenCV
def process_and_display(dicom_file_path):
    # Load the DICOM file
    dicom_data = pydicom.dcmread(dicom_file_path)

    # Extract DICOM pixel data as numpy array
    dicom_image = dicom_data.pixel_array

    # Apply mark_boundaries to enhance image boundaries
    if 'RescaleSlope' in dicom_data and 'RescaleIntercept' in dicom_data:
        slope = dicom_data.RescaleSlope
        intercept = dicom_data.RescaleIntercept
        hu_image = dicom_image * slope + intercept
    else:
        hu_image = dicom_image

    blurred_image = cv2.GaussianBlur(hu_image, (3, 3), 0)
    laplacian = cv2.Laplacian(blurred_image, cv2.CV_64F)
    sharpened_image = np.uint8(np.clip(blurred_image + laplacian, 0, 255))
    superpixel_edges = mark_boundaries(sharpened_image, np.zeros_like(dicom_image))

    # Display enhanced image using OpenCV
    cv2.imshow('Enhanced Image', superpixel_edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage with a single DICOM file
dicom_file_path = '../Data/ChimpIJ/IMG-0003-00513.dcm'
process_and_display(dicom_file_path)
