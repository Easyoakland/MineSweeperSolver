from functions import *
import pyautogui
import init

# TODO Refactor code to use a game class
# so all these functions don't need to pass every variable every time

# TODO change layout function to three separate functions for the 3 actions


# Define the possible cells there are
possibleCells = ["1.png", "2.png", "3.png", "4.png", "flag.png", "complete.png"]

# determine layout of board after confirming it was found
if determineLayout() == None:
    print("Couldn't find game")
    quit()
else:
    width, height, cellwidth, cellheight, origin, end, grid = determineLayout()

click((1, 1), grid, width)
# testing identify function
# print(identifyCell((1,1),grid,width,cellwidth,cellheight,possibleCells)
