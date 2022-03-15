from functions import *
import pyautogui
import init

# TODO Change identification function to use pixel color since identifyCell currently takes way too long

# TODO logic
# 1. If the number of cells is equal to the number on the tile then they are all bombs
# 2. If the number of bombs around a cell is equal to the cell the rest are not bombs
# 3. Implement linked cells


# TODO give cell a number of mines property
# iterate through grid creating a cell class instance for each

# remove artificial pausing. use ctrl-alt-delete if needed to abort program
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

game = Game()  # setup game class instance

# Define the possible cells there are
game.possibleCells = ["1.png", "2.png", "3.png",
                      "4.png", "flag.png", "cell.png", "complete.png"]

game.possibleCellToValueDict = {"1.png": 1, "2.png": 2, "3.png": 3,
                           "4.png": 4, "flag.png": -1, "cell.png": 9, "complete.png": 0}

# This is too slow to run ever logical cycle:
# make list of IDs for all cells
# cellArray = [game.identifyCellAtPos(pos) for i, pos in enumerate(game._grid)]

# pre-fill cellArray
game.cellArray = ["cell.png" for i in range(game._width*game._height)]

game.click((1, 1))

game.updateCellArray(Cell((1, 1), game))


# clear file contents
with open('temp.csv', 'w') as file:
    file.write("")

# testing updateCellArray
# write updateCellArray to file after formatting nicely
with open('temp.csv', 'a') as file:
    for i, cell in enumerate(game.cellArray):
        file.write(str(game.possibleCellToValueDict[cell])+", ")
        if (i+1) % (game._width) == 0:
            file.write("\n")
