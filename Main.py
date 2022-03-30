import init
from functions import *
import pyautogui
import cv2
from copy import deepcopy

# TODO guess occurs on empty lst (example is third failedgame state)

# TODO sometimes identifies cell as having a bomb on it
# TODO right edge is being handled weird and something is wrong
# on expert mode it always seems to flag the furthest right column from row 4-6
# TODO when it wins it gives an index error after guessing instead of realizing it won

# TODO logic
# 3.5. Implement linked cells
# partial overlap when overlap>= bombs in linkedCells
# 4. Probability?
# Either pick put a flag in a set where it is most likely there is a bomb (high prob num) or reveal a tile from a set that is most likely to be empty tile (low prob num)
# Guess where there are more intersecting sets because that will give the most information after guessing

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

linkedCellsLst = []  # saving all linked cells in a set so they aren't duplicated when added
# this loop ends if frontier is empty or if countdown is reached
# the second element will evaluate to false if the iterator goes larger than frontier twice
# the iterator is being used as a countdown to forcefully terminating loop
while (len(game.frontier) != 0 or len(linkedCellsLst) != 0):
    # if the frontier has an items to work on
    if len(game.frontier) != 0:
        currentCell = game.frontier.pop(0)  # pop off first element
        linkedCells = game.generateLinkedCells(currentCell)
        if linkedCells != None:  # if there was a linkedCells
            if game.linkedCellsRule1(linkedCells): # if rule 1 was able to do something currentCell
                continue  # the rest of the loop is unnecessary
            elif game.linkedCellsRule2(linkedCells): # if rule 2 was able to do something to the currentCell
                continue  # the rest of the loop is unnecessary
            else: # if neither rule could do something to the currentCell
                # add it to the list of linked cells
                linkedCellsLst.append(linkedCells)
                continue  # no need to check stored cells while there are more frontier cells to check
    elif len(linkedCellsLst) == 0:  # if this is also zero there is nothing left to do
        break
    elif len(linkedCellsLst) > 0:
        oldLength = 1
        newLength = 0
        # check to see if a previous linkedCells became solvable
        while oldLength > newLength:
            new_linkedCellsLst = linkedCellsLst.copy()  # make new list to copy results into
            # save current length for comparison at end of loop
            oldLength = len(linkedCellsLst)
            # simplify any linkedCell that can be simplified
            for i, linkedCells in enumerate(linkedCellsLst):
                # TODO discard using new_linkedCells doesn't work because they have different id
                new_linkedCells = deepcopy(linkedCells)
                # check to see if the linked cells now contain a flag or already checked cell
                for offset in linkedCells.linkedCellsOffsets:
                    tempID = game.recallCellID(game.convertOffsetToCord(offset))
                    if tempID == "flag.png":  # if the linked cells now contain a flag
                        new_linkedCells.linkedCellsOffsets.remove(
                            offset)  # remove the flag from the linkedCells
                        new_linkedCells.bombNum -= 1  # and decrease the amount of bombs left
                    elif tempID != "cell.png":  # if the linkedCells now contain an explored cell
                        # print("Detected explored in linkedCell at:"+ str(game.convertOffsetToCord(offset)))
                        # remove that tile as it obviously can't be one of the bombs anymore
                        # TODO not working randomly
                        new_linkedCells.linkedCellsOffsets.remove(offset)
                    # below shouldn't be true ever
                    if new_linkedCells.bombNum > len(new_linkedCells.linkedCellsOffsets):
                        print(
                            "ERROR at new_linkedCellsLst[" + str(i)+"] " + "has more bombs than cells to fill")
                # Check if logical operation can be done
                if game.linkedCellsRule1(new_linkedCells):
                    # instance of linkedCells is solved and no longer needed
                    new_linkedCellsLst[i] = 0 # replace with 0 so it is remembered but index is messed up
                elif game.linkedCellsRule2(new_linkedCells):
                    # instance of linkedCells is solved and no longer needed
                    new_linkedCellsLst[i] = 0 # replace with 0 so it is remembered but index is messed up
                else: # if no neither rule worked, still save any changed made to new_linkedCells
                    new_linkedCellsLst[i] = new_linkedCells
            # remove added 0's is safe now because i has reset so index's won't be out of sync
            new_linkedCellsLst = [item for item in new_linkedCellsLst if item != 0]
            # remove subset-superset overlaps
            game.removeCompleteOverlaps(new_linkedCellsLst)
            # removes any newly created empty lists
            new_linkedCellsLst = [item for item in new_linkedCellsLst if len(item.linkedCellsOffsets) != 0]
            linkedCellsLst = new_linkedCellsLst.copy()  # replace old lst with new one
            newLength = len(linkedCellsLst)  # get new length
        # nothing left to do if frontier wasn't added to after processing backlog
        if len(game.frontier) == 0:
            # Guess is Required so here is guess
            # TODO remove
            print("Guess was required")
            game.guess(linkedCellsLst)

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
