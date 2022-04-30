import init
from functions import *
import pyautogui
import cv2

# TODO linkedlists with flags in them aren't getting updated

# TODO the ERROR at new_linkedCellsLst[i] has more bombs than cells to fill will occur when it sees an unknown tile because it will still remove it from the linkedLst if it is unknown
# but if that tile is a bomb it will wind up removing too many and giving the error. Or if there is error in detection it will remove all cells of the linked list without removing the bombs

# TODO logic
# 3.5. Implement linked cells
# partial overlap when overlap or nonoverlap > bombs in linkedCells.
# 4. Probability?
# Either pick put a flag in a set where it is most likely there is a bomb (high prob num) or reveal a tile from a set that is most likely to be empty tile (low prob num)
# Guess where there are more intersecting sets because that will give the most information after guessing

# Each block loops through every position its parents haven't been where after one step it calls its children to do the same Once every position is permuted return to original position and tell parent to continue to parents next position.

# If two linkedcells intersect and the intersection contains less bombs than the size of the intersection then one of those intersections must be free. This means. ..

# For intersect numBombsInSet1NotIntersect= set1BobNum-(set2BobNum-NotIntersectNumSpacesOfSet2)

'''
-  if !deterministicSolve: guess
- validate combination
- while didsomething>0
- if !(deterministicSolve&&guess): game finished
- if guess: didsomething++
- if deterministic solve: didsomething++
'''

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
game.reveal((center))

# this loop ends if frontier is empty or if countdown is reached
# the second element will evaluate to false if the iterator goes larger than frontier twice
# the iterator is being used as a countdown to forcefully terminating loop
didSomething = 1
while didSomething > 0:
    didSomething = game.deterministicSolve()
    if didSomething <= 0: # if determinisic solution can't be preformed then guess
        if len(game.linkedCellsLst) != 0:  # if there are still linkedCells in linkedCellsLst
            # Guess is Required so here is guess
            print("Guess was required")
            if game.guess():
                didSomething +=1


# guess was required if the loop stopped but there victory isn't displayed
a = pyautogui.locateOnScreen("victory.png")
if a == None:
    print("Error - Can't continue")
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
