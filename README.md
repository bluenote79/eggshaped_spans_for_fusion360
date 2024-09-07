# Eggshaped spans for Fusion 360

## This skript adds spans calculated by Hügelschäffer equation to Fusion 360 fittin 3 splines ready for lofting.

<picture>

  <img alt="Illustrates usage of eggshaped spans for Fusion 360 script" src="https://github.com/bluenote79/eggshaped_spans_for_fusion360/blob/main/eggshaped_spans_for_fusion360/eggs.gif">

</picture>

Everyone using Fusion 360 probably knows this error message: *“The selected rail dos not touch all of the profiles.”*
To avoid this when lofting eggshaped spans I am working on this tool.

### Here are the steps to get it run:
1. In Fusion 360 go to Utilities > ADD-INS > Skripts and Add-Ins.
2. Create a new script (chose Script, Python and airfoil_to_line as Script Name
3. Right click on the script > Open file location
4. Overwrite the script with the [skript](https://github.com/bluenote79/eggshaped_spans_for_fusion360/blob/main/eggshaped_spans_for_fusion360/eggshaped_spans_for_fusion360.py) from here.

### Usage
1. The selectet splines must be top curve, bottom and middle (in that order)
2. You can chose the number of drawn points which will be multiplied by 4
3. Select origin Plane.
4. Choose the distance between spans, this must be a negative number if your splines go to negativ values in the coordinate system
5. Number of spans with equal distance
6. Choice to set the first span at 0.0 (only possible if the splines intersect this origin plane.
7. you can choose to give speciffic offset values seperated by semicolon, then you have to set "Abstand Spanten" to zero.

