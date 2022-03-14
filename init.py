import os

# This finds the abspath of the script executing
script_path = os.path.dirname(os.path.abspath(__file__))
# This sets the current path to be the script's path to allow for easy file use
os.chdir(script_path)
