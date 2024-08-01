# Symm-Drivers for Blender 4.2.0
This Blender add-on enables automatic symmetrization of drivers within transforms and constraints of selected bones, saving your valuable time.

Key Features:

-Supports multiple Armatures.
-Handles invalid drivers.

# How to use:
1.Locate the add-on in your computer folder through the menu Edit>Preferences>Add-on>Install...
2.Enter the EDIT MODE of the armature(s)
3.Select the bone(s) containing the driver
4.Make sure the bone(s) has a symmetrical counterpart
5.In the Armature menu, select the operator Symmetrize selected drivers
6.Save your precious time

# New version fix:

- Replace the equivalence dictionary with regex-based logic
- Correctly handle the letters l and r preceded and/or followed by '.', '-', '_'
- Ensure that the letters are not surrounded by other letters
- Simplify and optimize the symmetric bone name lookup function

