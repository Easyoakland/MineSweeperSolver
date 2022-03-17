import init
from functions import *
import pyautogui
import cv2

# TODO make setRecallCellID function for readability

# TODO logic
# 3. Implement linked cells
# Pop frontier cell and generate linked set from it. Don't add the cell back because all that matters is set collisions, mines in a set = len(set), and set.bombNum=0
# use sets to save all linked sets and set methods to compare with other sets
# If number of sets with no match = number of sets, a guess must be made
# If two linked sets with the same location exist, delete one of the duplicates. If they have different bomb nums but the same area return error
# If a set has less than 0 bombs return error
# 4. Probability?
# Naive probability is set.bombNum/len(set)
## Either pick put a flag in a set where it is most likely there is a bomb (high prob num) or reveal a tile from a set that is most likely to be empty tile (low prob num)
# Guess where there are more intersecting sets because that will give the most information after guessing
# 

# remove artificial pausing. use ctrl-alt-delete or alt-tab and ctrl-c if needed to abort program
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

game = Game()  # setup game class instance

# Define the possible cells there are
game.cellTypes = ["1.png", "2.png", "3.png",
                  "4.png", "5.png", "6.png", "7.png", "8.png", "flag.png", "cell.png", "complete.png"]

# save files to memory instead of repeatedly accessing them
for possibleCell in game.cellTypes:
    game.cellTypeIms.append(cv2.imread(possibleCell))

game.cellTypesDict = {"1.png": 1, "2.png": 2, "3.png": 3,
                      "4.png": 4, "5.png": 5, "6.png": 6, "7.png": 7, "8.png": 8, "flag.png": 9, "cell.png": 10, "complete.png": 11}

# pre-fill IDLst
game.IDLst = ["cell.png" for i in range(game._width*game._height)]

center = (int(game._width/2), int(game._height/2))
game.reveal(center)

i = 0
# game.frontier evaluates to true while frontier has an element
# the second element will evaluate to false if the iterator goes larger than frontier
# the iterator is being used as a countdown to forcefully terminating loop
while game.frontier and i < 2*len(game.frontier):
    i += 1
    currentCell = game.frontier.pop(0)  # pop off first element
    # run rule 1 and 2 and if both didn't do anything somethingHappened=False
    somethingHappened = game.rule1(currentCell) or game.rule2(currentCell)
    # if an action was performed reset loop countdown to forceful termination
    # this try loop will abort the inner for loop if currentCell is determined to still be part of the frontier
    if somethingHappened:
        i = 0
        continue  # no need to check if cell is still in frontier because it is known that it isn't
    # this will trigger from the raise in the if statement and break out of everything inside
    try:
        # for any neighbor of currentCell
        for neighbor in currentCell.neighbors(1, game._width, game._height):
            # if that cell is an unexplored cell
            if game.recallCellID(neighbor) == "cell.png":
                # then currentCell is still part of the frontier
                # Also don't need to check any other neighbors to see if they are also unrevealed so loop exited
                game.frontier.append(currentCell)
                # this is so it so inner for loop only adds back cell if it needs to be added but doesn't add it more than once
                raise ContinueOuterLoop
    except ContinueOuterLoop:
        pass

    # this tests how frontier changes
    # print("Frontier len: " + str(len(game.frontier)))

# guess was required if the loop stopped but there victory isn't displayed
a = pyautogui.locateOnScreen("victory.png")
if a == None:
    print("Guess was required")
else:
    print("VICTORY!")

# clear file contents
with open('FinalGrid.csv', 'w') as file:
    file.write("")

# testing updateIDLst
# write IDLst to file after formatting nicely
with open('FinalGrid.csv', 'a') as file:
    for i, cell in enumerate(game.IDLst):
        file.write(str(game.cellTypesDict[cell])+", ")
        if (i+1) % (game._width) == 0:
            file.write("\n")
