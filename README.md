# ENG Grid-Based Numbering for Revit

## Description
ENG Grid-Based Numbering is a PyRevit extension that automates the numbering of model elements in Revit based on their closest grid intersection. This tool is designed to streamline the process of numbering elements in large Revit projects while maintaining consistency with grid locations.

## Features
- Filter model elements by category.
- Select multiple elements for numbering.
- Choose a reference element to define the numbering sequence.
- Automatically assign grid intersections to elements.
- Visual progress bar during the numbering process.
- Works with shared parameters.

---

## Installation Guide

### 1. Ensure PyRevit is Installed
Before using this extension, ensure you have **PyRevit** installed. If you haven't installed it yet, follow these steps:

1. Download PyRevit from the official repository: [https://github.com/eirannejad/pyRevit](https://github.com/eirannejad/pyRevit)
2. Install it and ensure it's loaded into Revit.

### 2. Move the Extension to the PyRevit Folder
Copy the **eng.extension** folder into the PyRevit extensions directory:

#### Default locations:
- **Windows (default PyRevit extensions folder):**
  ```
  C:\Users\%USERNAME%\AppData\Roaming\pyRevit\Extensions\
  ```
- **Or, if installed globally:**
  ```
  C:\ProgramData\pyRevit\Extensions\
  ```

After copying, ensure the folder structure is:
```
C:\Users\%USERNAME%\AppData\Roaming\pyRevit\Extensions\eng.extension
```

### 3. Load the Extension in PyRevit
1. Open **Revit**.
2. Go to **PyRevit > Extensions Manager**.
3. Click **"Add Existing"** and navigate to the **eng.extension** folder.
4. Click **Load**.
5. Restart Revit to apply changes.

---

## How to Use

1. **Open the UI:**
   - Navigate to the **"Grid Tools"** panel in PyRevit.
   - Click the **"Grid-Based Numbering"** button.

2. **Filter by Category:**
   - Select the category of elements you want to number.

3. **Select Model Elements:**
   - Click **"Select Model Elements"** and choose the elements to be numbered.

4. **Select Reference Element:**
   - Click **"Select Start Element"** and choose an element to define the numbering order.

5. **Start Numbering:**
   - Click **"Start Numbering"** to execute the numbering process.
   - The tool will number elements and assign their nearest grid intersection.
   - A progress bar will show the completion status.

---

## Requirements
- **Revit 2019 or later**
- **PyRevit (latest version recommended)**
- **Shared parameters enabled in Revit**

---

## Troubleshooting

### 1. The extension does not appear in PyRevit
- Ensure the **eng.extension** folder is inside the correct PyRevit **Extensions** directory.
- Restart Revit after adding the extension.

### 2. The numbering does not apply correctly
- Make sure the elements selected belong to a category that allows numbering.
- Ensure the **shared parameters** file is correctly configured.

### 3. The progress bar does not update
- Restart Revit and try again.
- Ensure PyRevit is up to date.

---

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---


## Contact
Juan Sebastian Galindo Leal.

Githb User: SebBIMDeveloper
