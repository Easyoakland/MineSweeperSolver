from functions import *
import pyautogui
import init

# TODO Refactor code to use a game class
# so all these functions don't need to pass every variable every time

# TODO change layout function to three separate functions for the 3 actions

game = Game()

# Define the possible cells there are
game.possibleCells = ["1.png", "2.png", "3.png",
                      "4.png", "flag.png", "cell.png", "complete.png"]


game.click((1, 1))
print(game.identifyCell((1,1), game.possibleCells))