# FPSDataAnalyser (EN)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](https://github.com/June12138/ShooterGameStatAnalyser/blob/main/README.md)
# FPS Data Analyzer (EN)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/June12138/ShooterGameStatAnalyser/blob/main/README-EN.md)
## Introduction
FPSDataAnalyser is a small utility for analyzing FPS game data, capable of parsing .xlsx files and generating charts for different weapons at various distances. (e.g., TTK/distance, damage/distance, STK/distance, etc.)

Hovering over the charts will display specific values such as STK, damage, rate of fire, DPS, etc., making it convenient for comparison.
![alt text](screenshot.png)
## Usage
1. Download to local
2. CD to the project directory
3. Run in the terminal:
````
pip install -r requirements.txt
jupyter notebook
````
4. Run main.ipynb in the newly opened browser window. For subsequent runs, simply execute `jupyter notebook`.

## Settings Description
- All settings are in settings.xml
### In the sheet tag:
- **path** is the path to the .xlsx file;
- **sheetName** is the worksheet name;
- **idField** is the name of the id primary key field;
- **skipRows** is the number of rows the program needs to ignore (starting from zero, for example, if the first row of your table is a Chinese comment and the second row is the actual header, enter 0 to skip the first row);
- **separator** is the symbol used in the table to separate arrays (for example, if the damage distance and damage value in your table are separated by a space, enter a space).

### In the fieldNames tag:
- **idField** is the name of the id field;
- **name** is the name of the weapon field;
- **damageDistanceSegmentation** (optional) is the field name for the damage falloff segmentation distance (if you don&#39;t want to calculate falloff, leave it blank);
- **damageSegmentation** is the field name for the actual damage at different distances (support for calculating damage falloff based on damage multiplier will be added later);
- **bulletsPershot** is the field name for the number of bullets fired per attack;
- **fireRate** is the field name for the interval between each shot. s is the interval in seconds, ms is the interval in milliseconds, RPM is rounds per minute;
- **baseDamage** (optional) is the field name for the base damage. Required if damage falloff is calculated based on damage multiplier.

### In the general tag:
- **interpolation** is the interpolation mode for the charts drawn by the program, default is vh. Different interpolation methods include: hv, vh, hvh, vhv, spline, linear, see the official documentation&#39;s Interpolation section for details https://plotly.com/python/line-charts/;
- **health** is the preset health.
- **sizeX** is the width of the chart.
- **sizeY** is the height of the chart.

### In the units tag:
- **fireRate** is the unit for rate of fire, supporting s, ms (as the time interval between each shot), and RPM (rounds per minute);
- **damageSegmentationMode** is the damage falloff mode, supporting actual (actual damage) and multiplier (damage multiplier).

### In the graphSettings tag:
#### All supported **data names**:
STK, damage, fireInterval, fireRate, DPS, baseDamage
- **maxDistance** is the maximum distance displayed in the chart;
- **xAxis** is the attribute drawn on the x-axis (enter the data name);
- **yAxis** is the attribute drawn on the y-axis (enter the data name);
- **hoverFields** are the fields displayed in the hover window (data on the X/Y axes will be automatically displayed and does not need to be filled in, fill in other values to be displayed, separated by commas).

For specifics, you can refer to tables/Weapons.xlsx and compare it with settings.xml as a reference.