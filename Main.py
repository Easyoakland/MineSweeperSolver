import init
from functions import *
import pyautogui
import cv2
from copy import deepcopy

# TODO sometimes identifies cell as having a bomb on it

# TODO logic
# 3. Implement linked cells
# use sets to save all linked sets and set methods to compare with other sets
# If number of sets with no match = number of sets, a guess must be made
# If two linked sets with the same location exist, delete one of the duplicates. If they have different bomb nums but the same area return error
# If a set has less than 0 bombs return error
# 4. Probability?
# Naive probability is set.bombNum/len(set)
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

linkedCellsLst = [] # saving all linked cells in a set so they aren't duplicated when added
# this loop ends if frontier is empty or if countdown is reached
# the second element will evaluate to false if the iterator goes larger than frontier twice
# the iterator is being used as a countdown to forcefully terminating loop
while (len(game.frontier) != 0 or len(linkedCellsLst) != 0):
    #TODO remove next line it is just debugging
    # print("Start Frontier len: " + str(len(game.frontier)) + " Also, len(linkedCellsLst) is: " + str(len(linkedCellsLst)))
    if len(game.frontier) !=0:
        currentCell = game.frontier.pop(0)  # pop off first element
        linkedCells = game.generateLinkedCells(currentCell)
        if linkedCells != None: # if there was a linkedCells
            if game.linkedCellsRule1(linkedCells):
                continue # the rest of the loop is unnecessary
            elif game.linkedCellsRule2(linkedCells):
                continue # the rest of the loop is unnecessary
            else:
                linkedCellsLst.append(linkedCells) # add it to the list of linked cells
                continue # no need to check stored cells while there are more frontier cells to check
    elif len(linkedCellsLst) == 0: # if this is also zero there is nothing left to do
        break
    elif len(linkedCellsLst) > 0:
        oldLength = 1
        newLength = 0
        # check to see if a previous linkedCells became solvable
        while oldLength>newLength:
            new_linkedCellsLst = linkedCellsLst.copy() # make new list to copy results into
            oldLength = len(linkedCellsLst) # save current length for comparison at end of loop
            # simplify any linkedCell that can be simplified
            for i,linkedCells in enumerate(linkedCellsLst):
                # TODO discard using new_linkedCells doesn't work because they have different id
                new_linkedCells = deepcopy(linkedCells)
                # check to see if the linked cells now contain a flag or already checked cell
                for offset in linkedCells.linkedCellsOffsets:
                    tempID = game.recallCellID(game.convertOffsetToCord(offset))
                    if  tempID == "flag.png": # if the linked cells now contain a flag
                        new_linkedCells.linkedCellsOffsets.discard(offset) # remove the flag from the linkedCells
                        new_linkedCells.bombNum -=1 # and decrease the amount of bombs left
                    elif tempID != "cell.png": # if the linkedCells now contain an explored cell
                        # print("Detected explored in linkedCell at:"+ str(game.convertOffsetToCord(offset)))
                        new_linkedCells.linkedCellsOffsets.discard(offset) # remove that tile as it obviously can't be one of the bombs anymore
                    # below shouldn't be true ever
                    if new_linkedCells.bombNum > len(new_linkedCells.linkedCellsOffsets):
                        print("ERROR " + str(new_linkedCells) + "has more bombs than cells to fill")
                # Check if logical operation can be done
                if game.linkedCellsRule1(new_linkedCells):
                    new_linkedCellsLst[i] = 0 # instance of linkedCells is solved and no longer needed
                elif game.linkedCellsRule2(new_linkedCells):
                    new_linkedCellsLst[i] = 0 # instance of linkedCells is solved and no longer needed
            new_linkedCellsLst = [item for item in new_linkedCellsLst if item != 0] # remove added 0's
            game.removeCompleteOverlaps(new_linkedCellsLst) # remove subset-superset overlaps
            linkedCellsLst = new_linkedCellsLst.copy() # replace old lst with new one
            newLength = len(linkedCellsLst) # get new length
        if len(game.frontier) == 0: # nothing left to do if frontier wasn't added to after processing backlog
            break

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
