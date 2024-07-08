import numpy as np
import matplotlib.pyplot as plt
import os
import pydicom
from functions import detect_knee_bounding_boxes

# Function to read DICOM files in a folder in order and skip files before 400
def read_dicom_files(folder_path, start_point=400):
    dicom_files = []
    file_names = sorted(os.listdir(folder_path))  # Get all files in sorted order

    for file_name in file_names:
        if file_name.lower().endswith('.dcm'):
            file_label = int(file_name.split('-')[-1].split('.')[0])  # Extract the number after last hyphen
            if file_label >= start_point:
                dicom_files.append(os.path.join(folder_path, file_name))

    return dicom_files

# Function to process a DICOM file and get pixel count for <200 and >200 within bounding boxes
def process_dicom_file(dicom_file_path):
    # Load the DICOM file
    dicom_data = pydicom.dcmread(dicom_file_path)
    # Extract bounding boxes and multichannel image
    bounding_boxes, multichannel_image, edge_points = detect_knee_bounding_boxes(dicom_data)

    # Ensure exactly two bounding boxes are processed
    if len(bounding_boxes) != 2:
        return None

    # Initialize counts for each bounding box
    pixels_less_than_100_bb1 = 0
    pixels_greater_than_100_bb1 = 0
    pixels_less_than_100_bb2 = 0
    pixels_greater_than_100_bb2 = 0

    # Process each bounding box
    for i, box in enumerate(bounding_boxes):
        x1, y1, w, h = box
        x2, y2 = x1 + w, y1 + h
        # Crop the pixel array to the bounding box
        cropped_pixels = dicom_data.pixel_array[y1:y2, x1:x2].flatten()

        if i == 0:
            pixels_less_than_100_bb1 = np.sum(cropped_pixels < 250)
            pixels_greater_than_100_bb1 = np.sum(cropped_pixels >= 250)
        elif i == 1:
            pixels_less_than_100_bb2 = np.sum(cropped_pixels < 250)
            pixels_greater_than_100_bb2 = np.sum(cropped_pixels >= 250)

    return (pixels_less_than_100_bb1, pixels_greater_than_100_bb1), (pixels_less_than_100_bb2, pixels_greater_than_100_bb2)

# Folder containing the DICOM files
folder_path = '../Data/ChimpIJ/'

# Read and process each DICOM file in the folder
dicom_files = read_dicom_files(folder_path)

# Prepare data for plotting
file_labels = []
pixels_less_than_100_bb1_list = []
pixels_greater_than_100_bb1_list = []
pixels_less_than_100_bb2_list = []
pixels_greater_than_100_bb2_list = []

consectve_skip = 0

for dicom_file in dicom_files:
    file_name = os.path.basename(dicom_file)
    file_label = int(file_name.split('-')[-1].split('.')[0])  # Extract the number 530 from 'IMG-0002-00530.dcm'

    print(f"{file_label} ... ", end="")

    if consectve_skip > 100:
        break

    result = process_dicom_file(dicom_file)
    if result:
        (pixels_less_than_100_bb1, pixels_greater_than_100_bb1), (pixels_less_than_100_bb2, pixels_greater_than_100_bb2) = result

        file_labels.append(file_label)
        pixels_less_than_100_bb1_list.append(pixels_less_than_100_bb1)
        pixels_greater_than_100_bb1_list.append(pixels_greater_than_100_bb1)
        pixels_less_than_100_bb2_list.append(pixels_less_than_100_bb2)
        pixels_greater_than_100_bb2_list.append(pixels_greater_than_100_bb2)

        consectve_skip = 0

    else:
        consectve_skip += 1

    print("Done")

# Plotting the bar plots
x = np.arange(len(file_labels))  # Label locations
width = 0.35  # Width of the bars

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)  # Two subplots on the same window

# Plot for Bounding Box 1
bars1_bb1 = ax1.bar(x - width/2, pixels_less_than_100_bb1_list, width, label='Pixels < 200 (BB1)')
# bars2_bb1 = ax1.bar(x + width/2, pixels_greater_than_100_bb1_list, width, label='Pixels > 200 (BB1)')
ax1.set_ylabel('Number of Pixels')
ax1.set_title('Number of Pixels < 200 and > 200 by DICOM File (Bounding Box 1)')
ax1.legend()

# Plot for Bounding Box 2
bars1_bb2 = ax2.bar(x - width/2, pixels_less_than_100_bb2_list, width, label='Pixels < 200 (BB2)')
# bars2_bb2 = ax2.bar(x + width/2, pixels_greater_than_100_bb2_list, width, label='Pixels > 200 (BB2)')
ax2.set_xlabel('File Label (Last 3 Digits)')
ax2.set_ylabel('Number of Pixels')
ax2.set_title('Number of Pixels < 200 and > 200 by DICOM File (Bounding Box 2)')
ax2.legend()

# Set the x-axis labels for both plots with labels every 5 files
x_ticks = np.arange(0, len(file_labels), 5)
ax2.set_xticks(x_ticks)
ax2.set_xticklabels([file_labels[i] for i in x_ticks])

fig.tight_layout()
plt.show()
