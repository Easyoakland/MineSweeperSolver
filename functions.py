import pyautogui
from copy import deepcopy
from time import sleep

# how many times the board will be checked to have updated before deciding it won't update
timeoutAttemptsNum = 10

# This exists so the exception can be called to break to outer loop
# used by putting inner loop in a
# try:
# except ContinueOuterLoop:
# pass
# and doing "raise ContinueOuterLoop" when wanting to continue at outer loop


class ContinueOuterLoop(Exception):
    pass


# acts like enumerate but optionally takes value for start index and/or step of index
# to understand generators: https://www.youtube.com/watch?v=u3T7hmLthUU
def enumerateVariableIndex(toIterate, start=0, step=1):
    for item in toIterate:
        yield(start, item)
        start += step


# acts like enumerate but optionally takes value for start index and/or step
def enumerateVariableSpeed(toIterate, start=0, step=1):
    for i in range(len(toIterate)):
        if start >= len(toIterate):
            return
        yield(i, toIterate[start])
        start += step


# generator that turns a given sequence into one where using the INSTANCE_NAME.send(True) function on the generator restarts to the beginning of the sequence
def restartable(seq):
    while(True):
        for item in seq:
            restart = yield item
            if restart:
                break
        return


# Handles info about board itself
class Game:
    def __init__(self):
        # find properties of board after making sure board was found
        temp = self.determineLayout()
        if temp == None:  # if board wasn't found temp will have been set to None
            print("Couldn't find game")
            quit()
        else:
            self._width, self._height, self._cellwidth, self._cellheight, self._origin, self._end, self._grid = temp
        self.frontier = []  # initialize frontier que
        self.cellTypeIms = []  # initialize list to be filled with images of each cell type
        self.linkedCellsLst = []  # initialize list to be filled with unprocessed linkedCells

    def determineLayout(self):
        # First makes sure there was a recognized cell, then
        # set cell width and cell height using first identified cell's width and height
        # [2:4] is because the function outputs x,y,width,height and we only want width and height
        temp = pyautogui.locateOnScreen("cell.png")
        if temp != None:  # if temp is not none
            cellwidth, cellheight = temp[2:4]
        else:  # if temp is none
            return

        # get all cell locations and save to grid var
        grid = []
        for cell in pyautogui.locateAllOnScreen("cell.png"):
            grid.append(cell)

        # Find top left of map and set cords to origin
        origin = grid[0][0:2]
        # Find bottom right and set to end
        end = grid[-1][0:2]

        # set the width by counting how many cells into the offset the highest x value is
        # this only works if since the grid is square because this counts the width of the first row
        biggest = 0
        for i, cell in enumerate(grid):
            if cell[0] > biggest:
                biggest = cell[0]
                width = i+1
        # set the height by counting how many widths into the offset the highest y value is
        biggest = 0
        for i, cell in enumerateVariableSpeed(grid, step=width):
            if cell[1] > biggest:
                biggest = cell[1]
                height = i+1
        return int(width), int(height), int(cellwidth), int(cellheight), origin, end, grid

    # # iterates through all possible images to see if one matches
    # # if the image matches the if statement will be true and the image's string will be returned
    # def identifyCell(self, cord):
    #     pos = self.convertCordToPos(cord)
    #     for possibleCell in self.cellTypes:
    #         if pyautogui.locateOnScreen(possibleCell, region=(pos[0], pos[1], self._cellwidth, self._cellheight)) != None:
    #             return possibleCell
    #     return None

    # identify again but this time using a screenshot passed in instead for speed
    def identifyCell2(self, cord):
        # only unchecked cells can update so don't bother checking if it wasn't an unchecked cell last time it was updated
        temp = self.recallCellID(cord)
        if temp != "cell.png":
            return temp
        pos = self.convertCordToPos(cord)
        # return the first tiletype that matches the tile at the given cordinate
        for i, cellTypeIm in enumerate(self.cellTypeIms):
            if pyautogui.locate(cellTypeIm, self.boardIm, region=(pos[0]-self._origin[0], pos[1]-self._origin[1], self._cellwidth, self._cellheight), grayscale=True) != None:
                return self.cellTypes[i]
        print("UNIDENTIFIED CELL at cord: " + str(cord))
        return None

    # returns cached value for cell for faster ID time
    def recallCellID(self, cord):
        return self.IDLst[self.convertCordToOffset(cord)]

    # sets cached value for cell for better readability
    def setCellID(self, cord, ID):
        self.IDLst[self.convertCordToOffset(cord)] = ID

    # returns true if cord is flag
    def isFlag(self, offset):
        if "flag.png" == self.IDLst[offset]:
            return True
        return False

    # returns true if cord is number
    def isNumber(self, offset):
        for cellType in self.cellTypes[1:8]:  # check every numerical cell type
            if cellType == self.IDLst[offset]:
                return True
        return False

    # returns true if the cell is already identified as something
    def isExplored(self, offset):
        if self.IDLst[offset] != "cell.png":
            return True
        return False

    # convert grid cordinate to pixel position
    def convertCordToPos(self, cord):
        # offsets needed to get to each part of the cord in the grid list
        # this defines new cords have top left be 0, 0
        xOffset = cord[0]
        yOffset = self._width*cord[1]
        totalOffset = int(xOffset+yOffset)  # array indice must be of type int
        return self._grid[totalOffset][0:2]

    # convert pixel position to grid cordinate
    def convertPosToCord(self, pos):
        yCord = (pos[1]-self._origin[1])/self._cellheight
        xCord = (pos[0]-self._origin[0])/self._cellwidth
        return (int(xCord), int(yCord))

    # convert grid cord to offset
    def convertCordToOffset(self, cord):
        xOffset = cord[0]
        yOffset = self._width*cord[1]
        return int(xOffset+yOffset)

    # convert offset to cord
    def convertOffsetToCord(self, Offset):
        cnt = 0
        while Offset >= self._width:
            Offset = Offset-self._width
            cnt += 1
        y = cnt
        x = Offset
        # y = int(Offset/self._width)
        # x = int(Offset-y*self._width)
        return (x, y)

    # clicks at cell cordinate given
    def click(self, cord):
        pyautogui.click(self.convertCordToPos(cord))

    # right clicks at cell cordinate given
    def clickR(self, cord):
        pyautogui.click(self.convertCordToPos(cord), button="right")

    # click on pos given
    def clickPos(self, pos):
        pyautogui.click(pos)

    # cellTypes setter
    def setcellTypes(self, cellTypes):
        self._cellTypes = cellTypes

    # cellTypes getter
    def getcellTypes(self):
        return self._cellTypes

    # width getter
    def getWidth(self):
        return self._width

    # height getter
    def getHeight(self):
        return self._height

    cellTypes = property(getcellTypes, setcellTypes)

    # see if inputs can be optionally manual
    # screenshot board
    def setBoardScreenshot(self):
        self.boardIm = pyautogui.screenshot(region=(
            self._origin[0], self._origin[1], self._end[0]+self._cellwidth-self._origin[0], self._end[1]+self._cellheight-self._origin[1]))

    # find new cell IDs algorithm by
    # if cell's ID is different from array:
    # updating cell's ID in array if it is different,
    # if it is a number adding it to the frontier,
    # and if the cell is a complete, recursively check its neighbors the same way
    # else: do nothing since the cell is as expected from its ID in the IDLst
    def updateIDLst(self, cord):
        # only unchecked cells can update so don't bother checking if it wasn't an unchecked cell last time it was updated
        temp = self.recallCellID(cord)
        if temp != "cell.png":
            return
        cell = Cell(cord, self.identifyCell2(cord))
        # if cell ID is different from recorded for that cell
        if cell.ID != temp:
            # update ID record for that cell
            self.IDLst[self.convertCordToOffset(cell.cord)] = cell.ID
            if cell.ID == "complete.png":
                # updateIDLst on its neighbors
                for neighbor in cell.neighbors(1, self._width, self._height):
                    self.updateIDLst(neighbor)
            # if it is a number
            elif 0 < self.cellTypesDict[cell.ID] < 9:
                # add cell to frontier
                self.frontier.append(cell)
        # if it is a complete
        else:
            return

    # Reveal tile at cord then update cell Id's starting at clicked location
    def reveal(self, cord):
        self.click(cord)
        a = "cell.png"
        i = 0
        while a == "cell.png":  # this will keep looking for a change until one occurs
            if i >= timeoutAttemptsNum:  # if it must wait this many times
                print("Board won't update. Game Loss?")
                exit()
            # sleep(0.05)  # might be needed because pressed down tiles look kind of the same as unexplored cells, must wait for update and hope it did
            self.setBoardScreenshot()
            a = self.identifyCell2(cord)
            i += 1
        self.updateIDLst(cord)

    # Flag tile at cord then update cell Id at location to flag
    def flag(self, cord):
        # don't do anything if the cell isn't flaggable
        if self.recallCellID(cord) != "cell.png":
            print("tried flagging a non flaggable at:" + str(cord))
            return
        self.clickR(cord)
        self.setCellID(cord, "flag.png")

    # Logical Rule 1: If the number of unrevealed cells is equal to the number of bombs left around the cell then the unrevealed cells are bombs
    def rule1(self, cell):
        somethingHappened = False
        unrevealedCnt = 0
        flagCnt = 0
        # check neighbors of cell to see how many are unrevealed and how many are flags
        for neighbor in cell.neighbors(1, self._width, self._height):
            if self.IDLst[self.convertCordToOffset(neighbor)] == "cell.png":
                unrevealedCnt += 1
            elif self.IDLst[self.convertCordToOffset(neighbor)] == "flag.png":
                flagCnt += 1
        # if that number is the same as the number on this cell then all unrevealed cells are all bombs
        # if flag+unrevealed = total bombs around cell
        if flagCnt+unrevealedCnt == self.cellTypesDict[cell.ID]:
            for neighbor in cell.neighbors(1, self._width, self._height):
                # if neighboring cell is unrevealed
                if self.IDLst[self.convertCordToOffset(neighbor)] == "cell.png":
                    self.flag(neighbor)
                    somethingHappened = True  # return true if this changed the grid
        return somethingHappened

    # Logical Rule 2: If the number of flags around the cell equals the number of the cell all unrevealed cells are safe
    def rule2(self, cell):
        somethingHappened = False
        unrevealedCnt = 0
        flagCnt = 0
        # check neighbors of cell to see how many are flags
        for neighbor in cell.neighbors(1, self._width, self._height):
            if self.IDLst[self.convertCordToOffset(neighbor)] == "flag.png":
                flagCnt += 1
        # if the number of flags the same as the number on this cell then all unrevealed cells are all safe
        # check for flagCnt is equal to cell number
        if flagCnt == self.cellTypesDict[cell.ID]:
            for neighbor in cell.neighbors(1, self._width, self._height):
                # if neighboring cell is unrevealed
                if self.IDLst[self.convertCordToOffset(neighbor)] == "cell.png":
                    self.reveal(neighbor)
                    somethingHappened = True  # this did something so return true
        return somethingHappened

    # rule 1 implemented with sets. if the amount of bombs in a set is the same as the amount of cells in a set, they are all bombs
    def linkedCellsRule1(self, linkedCells):
        # if the number of bombs in the set is the same as the size of the set
        if linkedCells.bombNum == len(linkedCells.linkedCellsOffsets):
            # flag all cells in set
            for offset in linkedCells.linkedCellsOffsets:
                self.flag(self.convertOffsetToCord(offset))
            return True  # rule activated
        else:
            return False  # rule didn't activate

    # rule 2 implemented with sets. if the linkedCells has no bombs all cells in the set are safe
    def linkedCellsRule2(self, linkedCells):
        # if set of cells has no bomb
        if linkedCells.bombNum == 0:
            # reveal all cells in the set
            for offset in linkedCells.linkedCellsOffsets:
                self.reveal(self.convertOffsetToCord(offset))
            return True  # this rule activated
        else:
            return False  # didn't activate

    # generates a set for a given cell
    def generateLinkedCells(self, cell):
        setLoc = set()  # make a set for all locations given as an offset
        flagCnt = 0
        # for every neighbor of the given cell
        for neighbor in cell.neighbors(1, self._width, self._height):
            # if the neighbor is unexplored
            tempID = self.recallCellID(neighbor)
            if tempID == "cell.png":
                # add the offset to the set
                setLoc.add(self.convertCordToOffset(neighbor))
            elif tempID == "flag.png":  # if it is a flag
                flagCnt += 1  # add to the count for how many flags there are around this cell
        # if set is empty don't return anything because there is no valid linkedCells
        if len(setLoc) == 0:
            return None
        # the amount of bombs in the linkedCells is the amount there are around the cell minus how many have already been identified
        bombNum = self.cellTypesDict[cell.ID] - flagCnt
        return linkedCells(setLoc, bombNum)

    # takes a list of linkedCells and separates any subsets from supersets
    def removeCompleteOverlaps(self,new_linkedCellsLst):
        didSomething = False
        for i in range(len(new_linkedCellsLst)):
            # if set is flagged for deletion skip it
            if new_linkedCellsLst[i] == 0:
                continue
            # set to see if it is a subset
            set1 = new_linkedCellsLst[i].linkedCellsOffsets.copy()
            for j in range(len(new_linkedCellsLst)):
                # if set is flagged for deletion skip it
                if new_linkedCellsLst[j] == 0:
                    continue
                # set to see if it is a superset
                set2 = new_linkedCellsLst[j].linkedCellsOffsets
                if set1.issubset(set2) and (i != j):  # if it is an actual subset
                    # remove items that are shared from the superset
                    set2.difference_update(set1)
                    didSomething = True
                    # if len(set2) == 0:  # if this generated an empty set
                    #     # flag for removal. can't remove now because object is being iterated over and that would mess up index
                    #     new_linkedCellsLst[j] = 0
                    # else:  # if this didn't generate an empty set
                    # also decrease the bomb count of the superset by the subset's bombcount
                    new_linkedCellsLst[j].bombNum = new_linkedCellsLst[j].bombNum - \
                        new_linkedCellsLst[i].bombNum
        # remove what was flagged for removal now that looping isn't happening
        new_linkedCellsLst = [item for item in new_linkedCellsLst if len(item.linkedCellsOffsets) != 0]
        return didSomething, new_linkedCellsLst

    # finds probability that there is a bomb in target spot
    def probabilityOfBomb(self, linkedCells):
        return linkedCells.bombNum/len(linkedCells.linkedCellsOffsets)

    # Guess at best guess position
    # TODO make this take into account the amount of overlapped sets for breaking ties
    # TODO take into account that the lowest probability on a cell is the cell's actual probability of bomb if that cell is part of multiple linked lists
    def guess(self):
        didSomething = False
        maxSoFar = [0, 0]
        minSoFar = [101, 0]
        for i, linkedCells in enumerate(self.linkedCellsLst):
            # probability is a number from 0 to 1 here
            tempProbability = self.probabilityOfBomb(linkedCells)
            if maxSoFar[0] < tempProbability:
                maxSoFar = [tempProbability, i]
            if minSoFar[0] > tempProbability:
                minSoFar = [tempProbability, i]
        # if more certain about where a bomb isn't than where it is
        if maxSoFar[0] <= 1-minSoFar[0]:
            # then reveal a spot in the linkedCells with lowest odds of bomb
            self.reveal(self.convertOffsetToCord(
                list(self.linkedCellsLst[minSoFar[1]].linkedCellsOffsets)[0]))
            didSomething = True
        # if more certain about where a bomb is than where it isn't
        elif maxSoFar[0] > 1-minSoFar[0]:
            # then flag a spot in the linkedCells with the greatest chance of bomb
            self.flag(self.convertOffsetToCord(
                list(self.linkedCellsLst[maxSoFar[1]].linkedCellsOffsets)[0]))
            didSomething = True
        return didSomething

    def processFrontier(self):
        while len(self.frontier) > 0:
            currentCell = self.frontier.pop()  # pop off element
            linkedCells = self.generateLinkedCells(currentCell)
            if linkedCells != None:  # if there was a linkedCells
                # if rule 1 was able to do something currentCell
                if self.linkedCellsRule1(linkedCells):
                    continue  # the rest of the loop is unnecessary
                # if rule 2 was able to do something to the currentCell
                elif self.linkedCellsRule2(linkedCells):
                    continue  # the rest of the loop is unnecessary
                else:  # if neither rule could do something to the currentCell then add it to a list to apply more advanced techniques to later
                    # add it to the list of linked cells
                    self.linkedCellsLst.append(linkedCells)
                    continue

    # uses deterministic methods to solve the game
    def deterministicSolve(self):
        while len(self.frontier) > 0:
            self.processFrontier()
        didSomething = 1
        while len(self.linkedCellsLst) > 0 and didSomething > 0:
            didSomething = 0

            # simplify any linkedCell that can be simplified
            new_linkedCellsLst = self.linkedCellsLst.copy()  # make new list to copy results into
            for i, linkedCells in enumerate(self.linkedCellsLst):
                # make copy of current cell for edits later on
                new_linkedCells = deepcopy(linkedCells)

            # TODO split to function START -----------------------------------------------------------------------------------------
                # check to see if the linked cells now contain a flag or already checked cell
                for offset in linkedCells.linkedCellsOffsets:
                    if self.isFlag(offset):  # if the linked cells now contain a flag
                        new_linkedCells.linkedCellsOffsets.remove(
                            offset)  # remove the flag from the linkedCells
                        new_linkedCells.bombNum -= 1  # and decrease the amount of bombs left
                        didSomething += 1
                    # if the linkedCells now contain an explored cell
                    elif self.isExplored(offset):
                        # remove that tile as it obviously can't be one of the bombs anymore
                        new_linkedCells.linkedCellsOffsets.remove(offset)
                        didSomething += 1
                    # below shouldn't be true ever and detects errors
                    if new_linkedCells.bombNum > len(new_linkedCells.linkedCellsOffsets):
                        print(
                            "ERROR at new_linkedCellsLst[" + str(i)+"] " + "has more bombs than cells to fill")
            # TODO split to function END -----------------------------------------------------------------------------------------

            # TODO split to function START -----------------------------------------------------------------------------------------
                # Check if logical operation can be done
                if self.linkedCellsRule1(new_linkedCells):
                    # instance of linkedCells is solved and no longer needed
                    # replace with 0 so it is flagged for removal but index isn't messed up during self.linkedcellsLst enumeration
                    new_linkedCellsLst[i] = 0
                    didSomething += 1
                elif self.linkedCellsRule2(new_linkedCells):
                    # instance of linkedCells is solved and no longer needed
                    # replace with 0 so it is flagged for removal but index isn't messed up during self.linkedcellsLst enumeration
                    new_linkedCellsLst[i] = 0
                    didSomething += 1
                else:  # if no rule worked, still save any changed made to new_linkedCells
                    new_linkedCellsLst[i] = new_linkedCells
            # remove items flagged as 0's is safe now because i has reset so index won't be out of sync
            new_linkedCellsLst = [
                item for item in new_linkedCellsLst if item != 0]
            # TODO split to function END -----------------------------------------------------------------------------------------

            # remove subset-superset overlaps
            tmp, new_linkedCellsLst = self.removeCompleteOverlaps(new_linkedCellsLst)
            if tmp:
                didSomething += 1
            self.linkedCellsLst = new_linkedCellsLst.copy()  # replace old lst with new one
        return len(self.frontier) > 0
# Handles an individual cell on the board


class Cell:
    def __init__(self, cord, ID):
        self.ID = ID
        self.cord = cord

    # returns cords of all neighbors that exist
    def neighbors(self, radius, width, height):
        neighbors = []
        # goes from left to right and from top to bottom generating neighbor cords
        # each radius increases number of cells in each dimension by 2 starting with 1 cell at radius = 0
        for j in range(2*radius+1):
            for i in range(2*radius+1):
                neighbors.append(
                    (self.cord[0]-radius+i, self.cord[1]-radius+j))
        # removes self from neighbors list
        neighbors.remove(self.cord)
        # removes invalid neighbors
        i = 0
        while(i < len(neighbors)):
            cord = neighbors[i]
            # neighbor has negative cordinate
            if cord[0] < 0 or cord[1] < 0:
                neighbors.remove(cord)
                i -= 1  # move back since index of list will have shifted back
            # neighbor has cordinate larger than board
            elif cord[0] > width-1 or cord[1] > height-1:
                neighbors.remove(cord)
                i -= 1  # move back since index of list will have shifted back
            i += 1
        # returns neighbors list
        return neighbors


class linkedCells:
    def __init__(self, linkedCellsOffsets, bombNum):
        self.linkedCellsOffsets = linkedCellsOffsets
        self.bombNum = bombNum
