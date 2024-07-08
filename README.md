# AutoCobb

## What does the program do
The program runs by taking an input to a folder containing all the .dcm files for CTs of the Lower Extremities. Then it identifies the slice at resection depth. Following which it allows the user to draw a intersection line of the medial and lateral condyles. Lastly, it allows the user to refine points being selected and visualise the new Cobb's axis and metrics.

## How does the UI work?

<p align="center">
  <img src="https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/b8133f47-fea4-4a77-ac7b-2326ecc623b9" alt="Screen Recording">
</p>


<p align="center">
  <img src= "https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/blob/main/ScreenRecording2024-07-05at5.06.17PM-ezgif.com-video-to-gif-converter.gif", alt= "Screen Recording">
</p>

> [!TIP]
> The UI warns about potential angular differences between the planned Cobb's axis and the user's current access. More than 1 - 2 degrees of deviation would mean an incorrect Cobb's axis unless in cases with osteophytes. In cases where a point is on an osteophyte, it is alright to ignore this warning.

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
