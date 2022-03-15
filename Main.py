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

game = Game() # setup game class instance

# Define the possible cells there are
game.possibleCells = ["1.png", "2.png", "3.png",
                      "4.png", "flag.png", "cell.png", "complete.png"]

# make list of IDs for all cells
cellArray = [game.identifyCellAtPos(pos) for i, pos in enumerate(game._grid)]

print(cellArray)


cell1 = Cell((0, 0), game)
game.clickR((2, 2))
