from functions import *
import pyautogui
import init

# TODO Change identification function to use pixel color since identifyCell currently takes way too long

# TODO logic
# 3. Implement linked cells


# TODO give cell a number of mines property
# iterate through grid creating a cell class instance for each

# remove artificial pausing. use ctrl-alt-delete if needed to abort program
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

game = Game()  # setup game class instance

# Define the possible cells there are
game.possibleCells = ["1.png", "2.png", "3.png",
                      "4.png", "5.png", "6.png", "7.png", "8.png", "flag.png", "cell.png", "complete.png"]

game.possibleCellsDict = {"1.png": 1, "2.png": 2, "3.png": 3,
                                "4.png": 4, "5.png": 5, "6.png": 6, "7.png": 7, "8.png": 8, "flag.png": -1, "cell.png": 9, "complete.png": 0}

# This is too slow to run every logical cycle:
# make list of IDs for all cells
# cellArray = [game.identifyCellAtPos(pos) for i, pos in enumerate(game._grid)]

# pre-fill cellArray
game.cellArray = ["cell.png" for i in range(game._width*game._height)]

center = (int(game._width/2), int(game._height/2))
game.reveal(center)

somethingHappened = True
while somethingHappened:
    somethingHappened = False
    for i, ID in enumerate(game.cellArray):
        if ID == "flag.png" or ID == "cell.png" or ID == "complete.png":
            continue  # ignore non-numbered cells
        else:
            if (game.rule1(Cell(game.convertOffsetToCord(i), game))
                    or game.rule2(Cell(game.convertOffsetToCord(i), game))):
                somethingHappened = True
                # FOR TESTING
                # print("At a: " + ID + " Something happened near: " +
                #       str(game.convertOffsetToCord(i)))
                # continue
            # FOR TESTING
            # print("At a: " + ID + " Nothing happened near: " +
            #       str(game.convertOffsetToCord(i)))
    # print("Repeating" + str(somethingHappened))

# guess was required if the loop stopped but there victory isn't displayed
a = pyautogui.locateOnScreen("victory.png")
if a == None:
    print("Guess was required")

# clear file contents
with open('FinalGrid.csv', 'w') as file:
    file.write("")

# testing updateCellArray
# write updateCellArray to file after formatting nicely
with open('FinalGrid.csv', 'a') as file:
    for i, cell in enumerate(game.cellArray):
        file.write(str(game.possibleCellsDict[cell])+", ")
        if (i+1) % (game._width) == 0:
            file.write("\n")
