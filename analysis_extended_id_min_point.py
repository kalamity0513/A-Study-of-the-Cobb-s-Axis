import pickle
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Function to identify local minima and maxima
def identify_local_minima_and_maxima(metrics_values):
    metrics_values = np.array(metrics_values)
    # Find peaks (maxima)
    peaks, _ = scipy.signal.find_peaks(metrics_values, height=20000, distance=10, threshold=500)

    # Invert the smoothed metrics to find valleys (minima)
    troughs, _ = scipy.signal.find_peaks(metrics_values, height=[0, 20000], distance=10, threshold=[-10000, 10000])

    return peaks, troughs

# Function to filter local minima after the latest maxima
def filter_local_minima(peaks_bb1, minima_bb1, peaks_bb2, minima_bb2):
    # Identify the latest peak from both bounding boxes
    last_maxima_index_bb1 = peaks_bb1[-1] if len(peaks_bb1) > 0 else -1
    last_maxima_index_bb2 = peaks_bb2[-1] if len(peaks_bb2) > 0 else -1
    latest_peak_index = max(last_maxima_index_bb1, last_maxima_index_bb2)

    # Find all minima peaks after the latest peak index
    filtered_minima_bb1 = [minima for minima in minima_bb1 if minima > latest_peak_index]
    filtered_minima_bb2 = [minima for minima in minima_bb2 if minima > latest_peak_index]

    return filtered_minima_bb1, filtered_minima_bb2, latest_peak_index

# Function to find line segments meeting intensity criteria (7000 - 13000)
def find_line_segments(metrics_values, start_index, end_index, intensity_range):
    line_segments = []
    current_segment = []

    for i in range(start_index, end_index):
        if intensity_range[0] <= metrics_values[i] <= intensity_range[1]:
            current_segment.append((i, metrics_values[i]))
        else:
            if len(current_segment) > 5:  # Adjust as needed for minimum segment length
                line_segments.append(current_segment)
            current_segment = []

    # Check the last segment
    if len(current_segment) > 5:
        line_segments.append(current_segment)

    return line_segments

if __name__ == "__main__":

    # Load pickled data
    pickle_filename = 'results2.pickle'
    with open(pickle_filename, 'rb') as f:
        results = pickle.load(f)

    # Process each folder's results
    for folder_result in results:
        folder_name = folder_result['folder_name']
        folder_metrics = folder_result['results']

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

            prev_file_number = file_number

        if not gaps:
            continue

        # Extract file names and corresponding metrics values for both bounding boxes
        file_names = []
        for result in folder_metrics:
            file_names.append(result['file_name'])

            # Example metrics to process (using gray pixels for both bounding boxes)
            metrics_bb1 = result['metrics'][0]['gray_pixels']
            metrics_bb2 = result['metrics'][1]['gray_pixels']

            bounding_box_metrics1.append(metrics_bb1)
            bounding_box_metrics2.append(metrics_bb2)

        # Normalize file names for plotting
        file_names_numeric = np.arange(len(file_names))

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

            # Plotting both bounding boxes on the same plot
            plt.figure(figsize=(15, 6))  # Adjusted figsize for better x-axis readability
            plt.plot(file_names_numeric, bounding_box_metrics1, label='Gray Pixels (Bounding Box 1)', color='blue')
            plt.plot(file_names_numeric, bounding_box_metrics2, label='Gray Pixels (Bounding Box 2)', color='green')
            plt.plot(peaks_bb1, np.array(bounding_box_metrics1)[peaks_bb1], 'bo', label='Maxima (BB1)')
            plt.plot(peaks_bb2, np.array(bounding_box_metrics2)[peaks_bb2], 'go', label='Maxima (BB2)')
            plt.plot(filtered_minima_bb1, np.array(bounding_box_metrics1)[filtered_minima_bb1], 'r*', label='Filtered Minima (BB1)')
            plt.plot(filtered_minima_bb2, np.array(bounding_box_metrics2)[filtered_minima_bb2], 'y*', label='Filtered Minima (BB2)')

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
                    plt.plot(segment_indices, segment_values, 'r-', label='Line Segment (BB1)')
                    plt.plot(segment_indices, line_of_best_fit, 'r--')

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
                    plt.plot(segment_indices, segment_values, 'y-', label='Line Segment (BB2)')
                    plt.plot(segment_indices, line_of_best_fit, 'y--')

            if len(all_segments_indices_bb1) == 0 or len(all_segments_indices_bb2) == 0:
                plt.close()  # Close the plot if no valid segments found
                continue

            # Plot median line between minimum and maximum indices of all segments
            min_index = min(min(all_segments_indices_bb1), min(all_segments_indices_bb2))
            max_index = max(max(all_segments_indices_bb1), max(all_segments_indices_bb2))
            median_index = int(np.median([min_index, max_index]))
            plt.axvline(x=median_index, color='k', linestyle=':', label='Median Line')

            # Print the file name corresponding to the median index
            median_file_name = file_names[median_index]
            print(f"Median file name: {median_file_name}")

            plt.axvline(x=latest_peak_index, color='r', linestyle='--', label='Final Last Maxima')
            plt.xticks(file_names_numeric, file_names, rotation=45)
            plt.xlabel('File Names')
            plt.ylabel('Gray Pixels')
            plt.title(f'Maxima and Minima in Folder: {folder_name} (After Latest Peak)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except ValueError as e:
            print(f"Error processing folder {folder_name}: {e}")
