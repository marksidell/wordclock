## The Carbide 3D Designs

This directory contains all of the word clock Carbide 3D milling
designs (`*.c2d`) and GCode generated from the designs (`*.nc` files).

Except as noted:

- There is a .c2d and .nc file for each design.
- The origin for all designs is the lower-left corner of the piece.

| File | Description |
|------|-------------|
| `BackPanel`| The MDF back panel. |
| `BandBottom` | The bottom acrylic band. The design assumes the band is placed in a jig for milling, with the jig origin 24 mm to the left of and below the band lower left corner. The offset is the height of the band, allowing another piece of pre-cut band acrylic to be used to construct the jig. |
| `Bracket.c2d` | Both the top and bottom brackets in one design. The design is for half of the bracket, and assumes the bracket is milled in two operations, one for each side. |
| `BrackTop.nc` | The gcode for the top bracket. (The top bracket is symmetric.) |
| `BrackBottomLeft.nc` | The gcode for the left side of the bottom bracket. |
| `BrackTopRight.nc` | The gcode for the right side of the bottom bracket. |
| `CenterJig` | The center jig is used to position the brackets. This design is for the notch on the bottom of the jig to accomodate the power cord that loops through the bottom bracket. |
| `CornerJig` | The jig for milling the rounded corners on the back panel. |
| `CornerJigPreMerge.c2d` | The corner jig before the elements that form the curve have been joined. Handy if you want to tweak the design. |
| `LightSensorWell` | The well cut into the clock face for the light sensor. |
