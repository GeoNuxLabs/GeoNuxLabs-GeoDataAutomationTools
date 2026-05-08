<pre>
⠀⠀⠀⠀⠀⠀⠀⠀
  /$$$$$$                      /$$   /$$                     /$$                 /$$                
 /$$__  $$                    | $$$ | $$                    | $$                | $$                
| $$  \__/  /$$$$$$   /$$$$$$ | $$$$| $$ /$$   /$$ /$$   /$$| $$        /$$$$$$ | $$$$$$$   /$$$$$$$
| $$ /$$$$ /$$__  $$ /$$__  $$| $$ $$ $$| $$  | $$|  $$ /$$/| $$       |____  $$| $$__  $$ /$$_____/
| $$|_  $$| $$$$$$$$| $$  \ $$| $$  $$$$| $$  | $$ \  $$$$/ | $$        /$$$$$$$| $$  \ $$|  $$$$$$ 
| $$  \ $$| $$_____/| $$  | $$| $$\  $$$| $$  | $$  >$$  $$ | $$       /$$__  $$| $$  | $$ \____  $$ 
|  $$$$$$/|  $$$$$$$|  $$$$$$/| $$ \  $$|  $$$$$$/ /$$/\  $$| $$$$$$$$|  $$$$$$$| $$$$$$$/ /$$$$$$$/
 \______/  \_______/ \______/ |__/  \__/ \______/ |__/  \__/|________/ \_______/|_______/ |_______/ 
 
                                   Ｐｒｅｄｉｃｔｓ  ｔｏｍｏｒｒｏｗ
                            An initiative by Loa Andersson, Sweden 2025
</pre>

# GeoNuxLabs GeodataAutomationTools  
*Lightweight, practical Python tools for automating common geospatial workflows.*

---

## Important Notice

This repository contains standalone geospatial automation scripts.  
They may interact with local datasets, GDAL utilities, QGIS environments, or  
other geoprocessing tools installed on the user’s system.

Users are responsible for ensuring that:

- all input data is used in accordance with its licensing terms  
- processing results are validated before operational use  
- local system configurations (GDAL, QGIS, Python) are correctly maintained  

The authors assume **no responsibility** for data loss, incorrect processing  
results, or any operational consequences arising from the use of these tools.

---

## Overview

GeoNux_GeodataAutomationTools is a collection of small, focused Python scripts  
designed to simplify repetitive or time‑consuming geospatial tasks.  
The tools are intentionally modular and easy to adapt, making them suitable for:

- batch raster processing  
- vector housekeeping  
- QGIS/PyQGIS automation  
- directory‑based geodata workflows  
- experimentation and prototyping  

The repository is intended as a practical toolbox rather than a single  
application — each script solves one specific problem cleanly and transparently.

---

## Features

### ✔ Raster Processing Utilities  
- Batch mosaicking of DEM tiles  
- VRT creation  
- Reprojection helpers  
- NoData normalization  

### ✔ Vector Processing Helpers  
- CRS checks  
- Geometry validation  
- Attribute utilities  

### ✔ QGIS/PyQGIS Snippets  
- Layer management helpers  
- Processing‑framework wrappers  
- Project automation examples  

### ✔ General Workflow Tools  
- Directory scanning  
- File filtering  
- Logging templates  
- Reusable utility functions  

---

## Project Structure
```bash
GeoNux_GeodataAutomationTools/
│
├── scripts/
│   ├── raster/
│   ├── vector/
│   ├── qgis/
│   └── utilities/
│
├── dev/
│   └── experimental_snippets/
│
├── data/
│   └── sample_inputs/
│
├── LICENSE
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/GeoNux_GeodataAutomationTools.git
cd GeoNux_GeodataAutomationTools
```

### 2. Create a Python environment (recommended)
```bash
conda create -n geonux_tools python=3.12
conda activate geonux_tools
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage Guide
### 1. Select a Script

Navigate to the relevant folder under scripts/ and open the script you want to run.
Each script includes comments describing expected inputs and outputs.

### 2. Prepare Input Data

Most tools operate on:

- directory of raster tiles

- vector file

- QGIS project

- or paths defined directly in the script

### 3. Run the Script

From the project root or script directory:

```bash
python3 scripts/raster/mosaic_dem_tiles.py
```
For QGIS-script, easiest is to open the python-file in QGIS and run it from the python terminal.

### 4. Review Output

Processed files are written to the output directory defined in the script or
passed as an argument.
How It Works

The tools in this repository follow a simple design philosophy:

- Small, focused scripts that do one thing well

- Minimal dependencies to keep the tools portable

- Readable code intended for learning and reuse

- Modular functions that can be copied into -larger workflows

- Clear separation between scanning, processing, and writing steps

This makes the repository suitable both as a practical toolbox and as a
reference library for building more advanced automation pipelines.
Contributing

Contributions are welcome.
You may submit issues or pull requests to:

- add new automation scripts

- improve existing workflows

- enhance documentation

- fix bugs or edge cases

## License

This project is released under the MIT License.
You are free to use, modify, and distribute it.