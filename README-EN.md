# FPSDataAnalyser (EN)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](https://github.com/June12138/ShooterGameStatAnalyser/blob/main/README.md)
## Introduction
FPSDataAnalyser is a small tool designed for analyzing data from FPS (First-Person Shooter) games. It can parse .xlsx files and generate charts showing different weapons' performance at various distances (e.g., TTK/Distance, Damage/Distance, STK/Distance, etc.).

Hovering over the chart allows you to view specific numerical values, making it convenient to compare STK, damage, fire rate, DPS, etc.
![alt text](screenshot.png)
## Usage
1. Download to your local machine
2. Change directory to the project folder
3. Run in the terminal:
```
pip install -r requirements.txt
jupyter notebook
```
4. Run main.ipynb in the newly opened browser window. For subsequent runs, simply run `jupyter notebook`.

## Settings Explanation
- All settings are in the `settings.xml` file.
- In the `sheet` tag:
  - **path** is the path to the .xlsx file;
  - **sheetName** is the name of the worksheet;
  - **idField** is the name of the primary key field;
  - **skipRows** is the number of rows to be ignored by the program (starting from 0, e.g., if the first row of your table is a comment in Chinese and the second row is the actual header, fill in 0 to skip the first row);
  - **separator** is the symbol used to separate arrays in the table (e.g., if the damage distance and damage values are separated by spaces in your table, fill in a space).
- In the `fieldNames` tag:
  - **idField** is the name of the id field;
  - **name** is the name of the weapon name field;
  - **damageDistanceSegmentation** is the name of the field for the segmentation distance of damage attenuation;
  - **damageSegmentation** is the name of the field for actual damage at different distances (a mode to calculate damage attenuation by damage multiplier will be supported in the future);
  - **bulletsPershot** is the name of the field for the number of bullets fired per shot;
  - **fireRate** is the name of the field for the interval between shots (in seconds, and will also support microseconds and RPM as units of fire rate in the future).
- In the `general` tag:
  - **interpolation** is the interpolation mode for the tables drawn by the program, default is vh, with different interpolation methods including: hv, vh, hvh, vhv, spline, linear, for more details, see the official documentation on Interpolation: https://plotly.com/python/line-charts/;
  - **health** is the preset health.
- In the `units` tag:
  - **fireRate** is the unit of fire rate, supporting s (as the interval between shots), ms (as the interval between shots in milliseconds), and RPM (shots per minute).
- In the `graphSettings` tag:
  - **maxDistance** is the maximum distance displayed on the chart;
  - **xAxis** is the attribute drawn on the x-axis (usually distance);
  - **yAxis** is the attribute drawn on the y-axis (TTK, DPS, STK, etc.);
  - **hoverFields** are the fields displayed in the hover window (X/Y axis data will be automatically displayed, and additional fields such as STK, damage, shot interval, RPM, DPS are supported).

You can refer to `tables/Weapons.xlsx` and `settings.xml` for specific examples.