# AutoCobb

## Program Overview

AutoCobb is a tool designed to process CT scans of the lower extremities. It identifies the optimal slice at the resection depth, allows the user to draw an intersection line between the medial and lateral condyles, and provides functionality to refine selected points. The program visualizes the new Cobb's axis and relevant metrics for surgical pre-planning.

## How to Use

### Requirements

- Python 3.12
- Virtual environment (optional but recommended)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis.git
    cd A-Study-of-the-Cobb-s-Axis
    ```

2. Setup virtual environment (optional):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Activate the virtual environment
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Program

1. Navigate to the project directory:

    ```bash
    cd A-Study-of-the-Cobb-s-Axis
    ```

2. Run the program:

    ```bash
    python3 main_app.py [folder_name]  # Replace [folder_name] with your folder containing .dcm files
    ```

    If no folder name is provided, it defaults to 'Falcon'.

### User Interface (UI)

- **Slice Identification**: The user interface (UI) identifies the optimal axial tibial view slice at the resection depth with 62.5% accuracy across 8 test cases. 
- **DICOM Slider**: For the remaining cases, the selected slice is within 1 to 4 slices before or after the correct resection depth. To address this variability, an integrated DICOM slider enables users to adjust the slice using up or down arrows. 
- **Joint Line Drawing**: Enables the user to draw an intersection line between the medial and lateral condyles on the identified slice.
- **Cobb's Axis Visualization**: Provides tools to refine selected points and visualize the new Cobb's axis and metrics for surgical planning.
<p align="center">
  <img src="https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/b8133f47-fea4-4a77-ac7b-2326ecc623b9" alt="Screen Recording">
</p>

### Visual Workflow

![Visual Workflow](https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/dc94fa76-51d9-4201-8468-d3871a0bbccf)

### Notes

- **Joint Line Accuracy**: Currently, the joint line is drawn on the slice of the resection depth. Future updates may include drawing it on the slice showing the tibial spines for greater precision.
- **Performance**: Initial loading may take up to 3 minutes. Efforts are ongoing to reduce this time for improved usability.

> [!TIP]
> The UI alerts users to potential angular discrepancies between the planned Cobb's axis and the user's current alignment. Deviations exceeding 1 to 2 degrees may indicate an incorrect Cobb's axis, except in cases involving osteophytes. If a point lies on an osteophyte, this warning can be disregarded.
---

Feel free to customize and expand this template to suit your project's specific needs.

