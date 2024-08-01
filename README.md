# Symm-Drivers for Blender 4.2.0
This Blender add-on enables automatic symmetrization of drivers within transforms and constraints of selected bones, saving your valuable time.

#Key Features:

-Supports multiple Armatures.
-Handles invalid drivers.

# New version fix:

- Replace the equivalence dictionary with regex-based logic
- Correctly handle the letters l and r preceded and/or followed by '.', '-', '_'
- Ensure that the letters are not surrounded by other letters
- Simplify and optimize the symmetric bone name lookup function

# How to use:
-Locate the add-on in your computer folder through the menu Edit>Preferences>Add-on>Install...
-Enter the EDIT MODE of the armature(s)
-Select the bone(s) containing the driver
-Make sure the bone(s) has a symmetrical counterpart
-In the Armature menu, select the operator Symmetrize selected drivers
-Save your precious time
