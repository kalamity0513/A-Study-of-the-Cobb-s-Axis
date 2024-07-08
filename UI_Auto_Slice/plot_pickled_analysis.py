import pickle
import plotly.express as px
import pandas as pd

def plot_skipped_data(filename):
    # Load pickled data
    with open(filename, 'rb') as f:
        results = pickle.load(f)

    # Process results to handle skipped data points
    processed_data = []
    for folder_result in results:
        folder_name = folder_result['folder_name']
        folder_metrics = folder_result['results']


        absolute_data = []
        proportion_data = []

        for result in folder_metrics:
            absolute_data = []
            for metric in result['metrics']:
                # Process metrics here as needed
                # Example: Assume 'Value' is a list of values to plot
                values = metric['Value']

                # Handle skipped data points
                processed_values = []
                last_value = None
                for value in values:
                    if value is None:
                        if last_value is not None:
                            processed_values.append(last_value)
                    else:
                        processed_values.append(value)
                        last_value = value

                # Prepare data for plotting
                for i, value in enumerate(processed_values):
                    if value is None:
                        value = 0  # Show skipped points as 0
                        symbol = 'cross'
                        line_dash = 'dot'
                    else:
                        symbol = None
                        line_dash = None

                    absolute_data.append({
                        'Folder': folder_name,
                        'File': result['file_name'],
                        'Metric': 'Value',
                        'Index': i,
                        'Value': value,
                        'Symbol': symbol,
                        'LineDash': line_dash
                    })

            processed_data.extend(absolute_data)

    # Convert to DataFrame
    df = pd.DataFrame(processed_data)

    # Plotting
    fig = px.line(df, x='Index', y='Value', color='Folder', line_dash='LineDash', symbol='Symbol',
                  title='Skipped Data Points Plot', markers=True)
    fig.show()


def plot_metrics(filename):

    with open(filename, 'rb') as f:
        results = pickle.load(f)

        print(results)

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

# Example usage:
# try: plot_skipped_data('results.pickle')
# except: plot_metrics('results.pickle')
plot_metrics('results.pickle')
