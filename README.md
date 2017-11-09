# TINYsim
Simulation program for Conor McBride's TINY Machine.
![](https://user-images.githubusercontent.com/30571778/32622915-62d064a6-c57c-11e7-9242-d514947e9bec.png)
## How To Use
+ Run the script with Python 2.7
+ Input a TINY input queue in the format "x, x, x, x..."
+ Input a TINY configuration in the format "x x x x  xxxxxxxxxxxxxxx"
+ The program should then print a trace and state how the TINY program halted.

## Notes
+ This script halts after 500 operations, and assumes that the TINY program loops indefinitely
+ This can be changed by editing the main loop of the program, line 268. Set count to a desired value.
