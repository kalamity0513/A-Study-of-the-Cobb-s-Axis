import os
from typing import List
import pydicom
import numpy as np

from tqdm import tqdm
from datetime import datetime
from sklearn.linear_model import LinearRegression

from analysis_extended_id_min_point import filter_local_minima, find_line_segments, identify_local_minima_and_maxima
from analysis_script import calculate_metrics
from functions import detect_knee_bounding_boxes

def process_folder(folder_path: str) -> List:
    folder_name = os.path.basename(folder_path)
    results = []

    dicom_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dcm')]
    dicom_files.sort()

    steps = 1
    dicom_files = dicom_files[::steps]

    with tqdm(total=len(dicom_files), desc=f'Processing DICOM files in {folder_path}', unit=' files') as pbar:
        for dicom_file in dicom_files:
            dicom_data = pydicom.dcmread(dicom_file)
            bounding_boxes, _, _ = detect_knee_bounding_boxes(dicom_data)

            pbar.update(steps)

            if len(bounding_boxes) != 2:
                continue

            metrics = calculate_metrics(dicom_data.pixel_array, bounding_boxes)
            results.append({
                'file_name': os.path.basename(dicom_file),
                'metrics': metrics
            })


    return results


def process_metrics_from_data(file_names, dicom_data, bounding_boxes):
    results = []
    for i, dicom_data in enumerate(dicom_data):
        bounding_boxes = bounding_boxes[i]
        file_name = file_names[i]

        if len(bounding_boxes) != 2:
            continue

        metrics = calculate_metrics(dicom_data.pixel_array, bounding_boxes)
        results.append({
            'file_name': os.path.basename(file_name),
            'metrics': metrics
        })


    return results


def find_recc_file(folder_path, folder_metrics) -> int | None:
    folder_name = os.path.basename(folder_path)

    # Initialize lists to store metrics for both bounding boxes
    bounding_box_metrics1 = []
    bounding_box_metrics2 = []

    gaps = []
    prev_file_number = 0

    for i, result in enumerate(folder_metrics):
        file_name = (result['file_name'])
        file_number = int(file_name.split(".")[0][-3:])

        if prev_file_number + 100 <= file_number:
            gaps.append(i)

        # print(file_number)
        prev_file_number = file_number

    if not gaps:
        print("No Gaps")
        return None

    # Extract file names and corresponding metrics values for both bounding boxes
    file_names = []
    for result in folder_metrics:
        file_names.append(result['file_name'])

        # Example metrics to process (using gray pixels for both bounding boxes)
        metrics_bb1 = result['metrics'][0]['gray_pixels']
        metrics_bb2 = result['metrics'][1]['gray_pixels']

        bounding_box_metrics1.append(metrics_bb1)
        bounding_box_metrics2.append(metrics_bb2)

    try:
        # Identify local minima and maxima for both bounding boxes
        peaks_bb1, minima_bb1 = identify_local_minima_and_maxima(bounding_box_metrics1)
        peaks_bb2, minima_bb2 = identify_local_minima_and_maxima(bounding_box_metrics2)

        # Filter local minima after the latest maxima
        filtered_minima_bb1, filtered_minima_bb2, latest_peak_index = filter_local_minima(peaks_bb1, minima_bb1, peaks_bb2, minima_bb2)

        # Find line segments meeting intensity criteria (7000 - 13000) after the latest peak index
        intensity_range = (7000, 13000)
        line_segments_bb1 = find_line_segments(bounding_box_metrics1, gaps[0], gaps[1], intensity_range)
        line_segments_bb2 = find_line_segments(bounding_box_metrics2, gaps[0], gaps[1], intensity_range)

        # Plot identified line segments with best-fit lines and median line
        all_segments_indices_bb1 = []
        all_segments_indices_bb2 = []

        for segment in line_segments_bb1:
            if len(segment) < 5:
                continue  # Skip segments with fewer than 5 points

            segment_indices, segment_values = zip(*segment)

            # Perform linear regression
            segment_indices = np.array(segment_indices).reshape(-1, 1)
            model = LinearRegression().fit(segment_indices, segment_values)
            line_of_best_fit = model.predict(segment_indices)
            slope = model.coef_[0]
            average_height = np.mean(line_of_best_fit)
            if abs(slope) < 250 and 9000 <= average_height <= 12000:
                all_segments_indices_bb1.extend(segment_indices)

        for segment in line_segments_bb2:
            if len(segment) < 5:
                continue  # Skip segments with fewer than 5 points

            segment_indices, segment_values = zip(*segment)

            # Perform linear regression
            segment_indices = np.array(segment_indices).reshape(-1, 1)
            model = LinearRegression().fit(segment_indices, segment_values)
            line_of_best_fit = model.predict(segment_indices)
            slope = model.coef_[0]
            average_height = np.mean(line_of_best_fit)
            if abs(slope) < 250 and 9000 <= average_height <= 12000:
                all_segments_indices_bb2.extend(segment_indices)

        if len(all_segments_indices_bb1) == 0 or len(all_segments_indices_bb2) == 0:
            print("No Line Segments")
            return None

        # Plot median line between minimum and maximum indices of all segments
        min_index = min(min(all_segments_indices_bb1), min(all_segments_indices_bb2))
        max_index = max(max(all_segments_indices_bb1), max(all_segments_indices_bb2))
        median_index = int(np.median([min_index, max_index]))

        # Print the file name corresponding to the median index
        median_file_name = file_names[median_index]
        print(f"Median file name: {median_file_name}")

        return int(median_file_name.split(".")[0][-3:]) - 1

    except ValueError as e:
        print(f"Error processing folder {folder_name}: {e}")

if __name__ == "__main__":
    folder_path = "../Data/ChimpIJ"

    folder_metrics = process_folder(folder_path)
    find_recc_file(folder_path, folder_metrics)
