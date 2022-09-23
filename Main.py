import init
from functions import *
import pyautogui
from PIL import Image

# Installation requires `pip install pyautogui`, `pip install pillow`, `pip install opencv-python`, `pip install mss`


# remove artificial pausing. use ctrl-alt-delete or alt-tab and ctrl-c if needed to abort program
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

game = Game()  # setup game class instance

# Define the possible cells there are
game.cellTypes = ["1.png", "2.png", "3.png",
                  "4.png", "5.png", "6.png", "7.png", "8.png", "flag.png", "cell.png", "complete.png"]

# save files to memory instead of repeatedly accessing them
for possibleCell in game.cellTypes:
    game.cellTypeIms.append(Image.open(possibleCell))

game.cellTypesDict = {"1.png": 1, "2.png": 2, "3.png": 3,
                      "4.png": 4, "5.png": 5, "6.png": 6, "7.png": 7, "8.png": 8, "flag.png": 9, "cell.png": 10, "complete.png": 11}

# pre-fill IDLst
game.IDLst = ["cell.png" for i in range(game._width*game._height)]

center = (int(game._width/2), int(game._height/2))
game.reveal((center))

# this loop will keep going until nothing happens when it runs
didSomething = 1
while didSomething > 0:
    for _ in range(20):
        didSomething = game.deterministicSolve()

    # if there are still linkedCells in linkedCellsLst
    if len(game.linkedCellsLst) != 0:
        # Guess is Required so here is guess
        print("Guess was required")
        if game.probabalisticGuess() >= 1:
            print("probabilistic guess used")
            didSomething += 1
            continue  # don't guess again if this worked
        if game.guess() >= 1:
            print("fast guess used")
            didSomething += 1


# If the loop stopped either won or lost
a = pyautogui.locateOnScreen("victory.png")
if a == None:
    print("Loss.")
else:
    print("VICTORY!")

exiting(game)
