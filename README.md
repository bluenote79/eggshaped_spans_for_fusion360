# Eggshaped spans for Fusion 360

## This skript adds spans calculated by Hügelschäffer equation to Fusion 360 fittin 3 splines ready for lofting.

<picture>

  <img alt="https://www.rc-network.de/attachments/py-gif">

</picture>

Everyone using Fusion 360 probably knows this error message: *“The selected rail dos not touch all of the profiles.”*
To avoid this when lofting spans I am working on this tool.

### Here are the steps to get it run:
1. In Fusion 360 go to Utilities > ADD-INS > Skripts and Add-Ins.
2. Create a new script (chose Script, Python and airfoil_to_line as Script Name
3. Right click on the script > Open file location
4. Rename the “make_bat_for_module_install_to_subfolder.py” to “airfoil_to_line.py” an insert it in the script folder.
5. Run the script to get the bat-file. It includes:
start cmd /K <path to Fusions python>\python -m pip install --target <path to lib folder in scriptfolder> --upgrade pyfoil
6. Shut down Fusion 360
7. Run the bat file
8. Run Fusion an overwrite the script with the aiforil_to_line.py script.
