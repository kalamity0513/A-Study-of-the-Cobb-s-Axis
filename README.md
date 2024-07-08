# AutoCobb

## Program Overview
The program operates by taking as input a folder containing all .dcm files for CT scans of the lower extremities. It identifies the slice at the resection depth, then allows the user to draw an intersection line of the medial and lateral condyles, which is the only user input required. Finally, the program enables the user to refine the selected points and visualize the new Cobb's axis and metrics for surgical pre-planning.

## How does the UI work?

<p align="center">
  <img src="https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/b8133f47-fea4-4a77-ac7b-2326ecc623b9" alt="Screen Recording">
</p>

> [!TIP]
>The user interface (UI) identifies the optimal axial tibial view slice at the resection depth with 62.5% accuracy across 8 test cases. For the remaining cases, the selected slice is within 1 to 4 slices before or after the correct resection depth. To address this variability, an integrated DICOM slider enables users to adjust the slice using up or down arrows.
> The UI alerts users to potential angular discrepancies between the planned Cobb's axis and the user's current alignment. Deviations exceeding 1 to 2 degrees may indicate an incorrect Cobb's axis, except in cases involving osteophytes. If a point lies on an osteophyte, this warning can be disregarded.

## Visual Workflow
![image](https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/dc94fa76-51d9-4201-8468-d3871a0bbccf)

## How to run it?
**Steps**
- Activate virtual environment
- Run program providing folder

```bash
source .venv/bin/activate # use whichever venv appropriate for your shell
python3 main_app.py [folder_name] # folder name is optional, defaults to Falcon
python
```
> [!CAUTION]
> The joint line is drawn here on the slice of the resection depth but ideally, it should be done on the slice that show the tibial spines as to be very accurate. This could be a potential update to the UI.
