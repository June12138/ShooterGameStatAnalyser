# FPSDataAnalyser (EN)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](https://github.com/June12138/ShooterGameStatAnalyser/blob/main/README-CN.md)
## Introduction
FPSDataAnalyser is a small tool for analyzing FPS game data, which can parse .xlsx files and generate charts of different weapons at different distances. (Currently only TTK charts, but it's easy to modify the code to generate other charts.)

Hovering over the chart will show the specific values, such as STK, damage, and fire rate, which is convenient for comparison.
![alt text](screenshot.png)
## Usage
1. Download to local
2. CD to the project directory
3. Run in the terminal:
```
pip install -r requirements.txt
jupyter notebook
```
4. Run main.ipynb in the newly opened browser window. Run jupyter notebook directly the second time.

## Settings
- All settings are in settings.xml
- sheet tag,
  - **path** is the .xlsx file path;
  - **sheetName** is the name of the worksheet;
  - **idField** is the name of the id primary key field;
  - **skipRows** is the number of rows that the program needs to ignore (starting from zero, for example, if the first row of your table is a comment in Chinese and the second row is the actual table header, fill in 0 to skip the first row);
  - **separator** is the symbol used to separate arrays in the table (for example, if the damage distance and damage value in your table are separated by spaces, fill in a space).
  - **interpolation** is the interpolation mode of the table drawn by the program, default vh, different interpolation modes can be found on the plotly official website.
  - **health** is the preset health.

For more details, please refer to tables/Weapons.xlsx.