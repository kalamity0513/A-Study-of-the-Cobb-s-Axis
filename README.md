![Static Badge](https://img.shields.io/badge/status-in_progress-red?style=flat&labelColor=%237fb3d5&color=%231a5276)

# How does the UI work?
<p align="center">
  <img src="https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/b8133f47-fea4-4a77-ac7b-2326ecc623b9" alt="Screen Recording">
</p>
> [!TIP]
> The UI warns about potential angular differences between the planned Cobb's axis and the user's current access. More than 1 - 2 degrees of deviation would mean an incorrect Cobb's axis unless in cases with osteophytes. In cases where a point is on an osteophyte, it is alright to ignore this warning.

# Visual Workflow
![image](https://github.com/kalamity0513/A-Study-of-the-Cobb-s-Axis/assets/115133535/dc94fa76-51d9-4201-8468-d3871a0bbccf)

# How to run it?
In **_main_app.py_**, replace the variable **_image_path_** with the respective file path of the _.dcm_ image slice
```
image_path = "/*.dcm"
```
> [!CAUTION]
> The joint line is drawn here on the slice of the resection depth but ideally, it should be done on the slice that show the tibial spines as to be very accurate. This could be a potential update to the UI. 


