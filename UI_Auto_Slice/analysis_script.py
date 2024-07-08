folder_path = '../Data/ChimpIJ'
folder_paths = ['../Data/ChimpIJ', "../Data/FalconIJ", "../Data/IguanaIJ", "../Data/ArmadilloIJ", "../Data/KangarooIJ", "../Data/LLamaIJ", "../Data/OctopusIJ", "../Data/NumbatIJ"]
# folder_paths = ['../Data/GorillaIJ', "../Data/KangarooIJ", "../Data/ArmadilloIJ"]

import os
import pydicom
import numpy as np
import plotly.express as px
import pandas as pd
import pickle

from functions import detect_knee_bounding_boxes

def calculate_metrics(image, bounding_boxes):
    metrics = []
    for box in bounding_boxes:
        x, y, w, h = box
        bbox_image = image[y:y+h, x:x+w]
        total_pixels = w * h

        # Compute dynamic thresholds using percentiles
        flattened = bbox_image.flatten()
        white_threshold = np.percentile(flattened, 99)
        black_threshold = np.percentile(flattened, 1)
        almost_white_threshold = np.percentile(flattened, 95)
        almost_black_threshold = np.percentile(flattened, 5)

        white_pixels = np.sum(bbox_image >= white_threshold)
        black_pixels = np.sum(bbox_image <= black_threshold)
        almost_white_pixels = np.sum((bbox_image >= almost_white_threshold) & (bbox_image < white_threshold))
        almost_black_pixels = np.sum((bbox_image > black_threshold) & (bbox_image <= almost_black_threshold))
        gray_pixels = np.sum((bbox_image > almost_black_threshold) & (bbox_image < almost_white_threshold))

        area = w * h
        metrics.append({
            'total_pixels': total_pixels,
            'white_pixels': white_pixels,
            'almost_white_pixels': almost_white_pixels,
            'gray_pixels': gray_pixels,
            'almost_black_pixels': almost_black_pixels,
            'black_pixels': black_pixels,
            'area': area,
            'white_proportion': white_pixels / total_pixels,
            'almost_white_proportion': almost_white_pixels / total_pixels,
            'gray_proportion': gray_pixels / total_pixels,
            'almost_black_proportion': almost_black_pixels / total_pixels,
            'black_proportion': black_pixels / total_pixels
        })
    return metrics

def process_folders(folder_paths):
    all_results = []
    for folder_path in folder_paths:

        folder_name = os.path.basename(folder_path)
        print(f"####### DATA: {folder_name} #######")

        results = []

        dicom_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.dcm')]
        dicom_files.sort()
        steps = 1
        dicom_files = dicom_files[::steps]

        index = 0

        for dicom_file in dicom_files:
            dicom_data = pydicom.dcmread(dicom_file)
            bounding_boxes, multichannel_image, edge_points = detect_knee_bounding_boxes(dicom_data)

            print(f"{index * steps + 1} ... ", end="")
            index += 1

            if len(bounding_boxes) != 2:
                print("Skipped")
                continue

            metrics = calculate_metrics(dicom_data.pixel_array, bounding_boxes)
            results.append({
                'file_name': os.path.basename(dicom_file),
                'metrics': metrics
            })

            print("Done")

        all_results.append({
            'folder_name': folder_name,
            'results': results
        })

        print("")

    return all_results

def plot_metrics(results):
    for folder_result in results:
        folder_name = folder_result['folder_name']
        folder_metrics = folder_result['results']

        absolute_data = []
        proportion_data = []

        for result in folder_metrics:
            left_box_metrics = result['metrics'][0]
            right_box_metrics = result['metrics'][1]

            absolute_data.extend([
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'White Pixels', 'Value': left_box_metrics['white_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Almost White Pixels', 'Value': left_box_metrics['almost_white_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Gray Pixels', 'Value': left_box_metrics['gray_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Almost Black Pixels', 'Value': left_box_metrics['almost_black_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Black Pixels', 'Value': left_box_metrics['black_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'White Pixels', 'Value': right_box_metrics['white_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Almost White Pixels', 'Value': right_box_metrics['almost_white_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Gray Pixels', 'Value': right_box_metrics['gray_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Almost Black Pixels', 'Value': right_box_metrics['almost_black_pixels']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Black Pixels', 'Value': right_box_metrics['black_pixels']}
            ])

            proportion_data.extend([
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'White Proportion', 'Value': left_box_metrics['white_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Almost White Proportion', 'Value': left_box_metrics['almost_white_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Gray Proportion', 'Value': left_box_metrics['gray_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Almost Black Proportion', 'Value': left_box_metrics['almost_black_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Left', 'Metric': 'Black Proportion', 'Value': left_box_metrics['black_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'White Proportion', 'Value': right_box_metrics['white_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Almost White Proportion', 'Value': right_box_metrics['almost_white_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Gray Proportion', 'Value': right_box_metrics['gray_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Almost Black Proportion', 'Value': right_box_metrics['almost_black_proportion']},
                {'Folder': folder_name, 'File': result['file_name'], 'Box': 'Right', 'Metric': 'Black Proportion', 'Value': right_box_metrics['black_proportion']}
            ])

        # Convert to DataFrames for Plotly
        df_absolute = pd.DataFrame(absolute_data)
        df_proportion = pd.DataFrame(proportion_data)

        # Plotting absolute pixel counts
        fig_absolute = px.line(df_absolute, x='File', y='Value', color='Metric', line_dash='Box',
                               title=f'Absolute Pixel Metrics for Bounding Boxes - {folder_name}', markers=True)
        fig_absolute.show()

        # Plotting proportion pixel counts
        # fig_proportion = px.line(df_proportion, x='File', y='Value', color='Metric', line_dash='Box',
        #                          title=f'Proportion Pixel Metrics for Bounding Boxes - {folder_name}', markers=True)
        # fig_proportion.show()


if __name__ == "__main__":
    results = process_folders(folder_paths)

    # Plotting and printing metrics for each folder
    plot_metrics(results)

    # After generating `results` list
    with open('results2.pickle', 'wb') as f:
        pickle.dump(results, f)
