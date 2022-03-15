import pyautogui
from time import sleep

# click top left cell
# pyautogui.click(grid[0])

# click top right cell
# pyautogui.click(grid[width-1])

# click second row on the right
# pyautogui.click(grid[(2*width)-1])


# acts like enumerate but optionally takes value for start index and/or step of index
# to understand generators: https://www.youtube.com/watch?v=u3T7hmLthUU
def enumerateVariableIndex(toIterate, start=0, step=1):
    for item in toIterate:
        yield(start, item)
        start += step


def enumerateVariableSpeed(toIterate, start=0, step=1):
    for i in range(len(toIterate)):
        if start >= len(toIterate):
            return
        yield(i, toIterate[start])
        start += step


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

    # iterates through all possible images to see if one matches
    # if the image matches the if statement will be true and the image's string will be returned
    def identifyCell(self, cord):
        pos = self.convertCordToPos(cord)
        for possibleCell in self.possibleCells:
            if pyautogui.locateOnScreen(possibleCell, region=(pos[0], pos[1], self._cellwidth, self._cellheight)) != None:
                return possibleCell
        return None

    # identify again but this time using a screenshot passed in instead
    def identifyCell2(self, cord, boardIm):
        pos = self.convertCordToPos(cord)
        for possibleCell in self.possibleCells:
            if pyautogui.locate(possibleCell, boardIm, region=(pos[0]-self._origin[0], pos[1]-self._origin[1], self._cellwidth, self._cellheight)) != None:
                return possibleCell
        return None

    # same as identify cell but takes pixel location
    def identifyCellAtPos(self, pos):
        for possibleCell in self.possibleCells:
            if pyautogui.locateOnScreen(possibleCell, region=(pos[0], pos[1], self._cellwidth, self._cellheight)) != None:
                return possibleCell
        return None

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
        while Offset > self._width:
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

    # possibleCells setter
    def setPossibleCells(self, possibleCells):
        self._possibleCells = possibleCells

    # possibleCells getter
    def getPossibleCells(self):
        return self._possibleCells

    # width getter
    def getWidth(self):
        return self._width

    # height getter
    def getHeight(self):
        return self._height

    possibleCells = property(getPossibleCells, setPossibleCells)

    # screenshot board
    def boardScreenshot(self, boardIm=None):
        if boardIm == None:  # if no image of the board was given, get one
            boardIm = pyautogui.screenshot(region=(
                self._origin[0], self._origin[1], self._end[0]+self._cellwidth-self._origin[0], self._end[1]+self._cellheight-self._origin[1]))
        return boardIm

    # find new cell IDs algorithm
    def updateCellArray(self, cord, boardIm=None):
        boardIm = self.boardScreenshot(boardIm=boardIm)
        cell = Cell(cord, self, boardIm)
        # if cell has updated
        if self.cellArray[self.convertCordToOffset(cell.cord)] != cell.ID:
            self.cellArray[self.convertCordToOffset(
                cell.cord)] = cell.ID  # update its ID
            # check neighbors of updated cell to see if they also updated
            for neighbor in cell.neighbors(1, self):
                if cell.ID != "complete.png":  # no need to check neighbors of a non complete cell because new cells must be touching completed cells
                    continue  # so skip this neighbor and go to next
                self.updateCellArray(neighbor)
        else:
            return

    # Reveal tile at cord then update cell Id's starting at clicked location
    def reveal(self, cord):
        self.click(cord)
        sleep(0.1)
        self.updateCellArray(cord)

    # Flag tile at cord then update cell Id at location to flag
    def flag(self, cord):
        self.clickR(cord)
        self.cellArray[self.convertCordToOffset(cord)] = "flag.png"

    # Logical Rule 1: If the number of unrevealed cells is equal to the number of bombs left around the cell then the unrevealed cells are bombs
    def rule1(self, cell):
        unrevealedCnt = 0
        flagCnt = 0
        # check neighbors of cell to see how many are unrevealed and how many are flags
        for neighbor in cell.neighbors(1, self):
            if self.cellArray[self.convertCordToOffset(neighbor)] == "cell.png":
                unrevealedCnt += 1
            elif self.cellArray[self.convertCordToOffset(neighbor)] == "flag.png":
                flagCnt += 1
        # if that number is the same as the number on this cell then all unrevealed cells are all bombs
        # if flag+unrevealed = total bombs around cell
        if flagCnt+unrevealedCnt == self.possibleCellToValueDict[cell.ID]:
            for neighbor in cell.neighbors(1, self):
                # if neighboring cell is unrevealed
                if self.cellArray[self.convertCordToOffset(neighbor)] == "cell.png":
                    self.flag(neighbor)
            return cell
        else: #if that number is different and this didn't do anything
            return None


    # Logical Rule 2: If the number of flags around the cell equals the number of the cell all unrevealed cells are safe
    def rule2(self, cell):
        unrevealedCnt = 0
        flagCnt = 0
        # check neighbors of cell to see how many are flags
        for neighbor in cell.neighbors(1, self):
            if self.cellArray[self.convertCordToOffset(neighbor)] == "flag.png":
                flagCnt += 1
        # if the number of flags the same as the number on this cell then all unrevealed cells are all safe
        # check for flagCnt is equal to cell number
        if flagCnt == self.possibleCellToValueDict[cell.ID]:
            for neighbor in cell.neighbors(1, self):
                # if neighboring cell is unrevealed
                if self.cellArray[self.convertCordToOffset(neighbor)] == "cell.png":
                    self.reveal(neighbor)


# Handles an individual cell on the board
class Cell:
    def __init__(self, cord, Game, boardIm=None):
        boardIm = Game.boardScreenshot(boardIm=boardIm)
        self._ID = Game.identifyCell2(cord, boardIm)
        self.cord = cord
        # self._width, self._height = Game.getWidth(), Game.getHeight()

    # returns cords of all neighbors that exist
    def neighbors(self, radius, game):
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
            elif cord[0] > game._width-1 or cord[1] > game._height-1:
                neighbors.remove(cord)
                i -= 1  # move back since index of list will have shifted back
            i += 1
        # returns neighbors list
        return neighbors

    # set ID
    def setID(self, game):
        self._ID = Game.identifyCell2(self.cord, boardIm)

    # get ID
    def getID(self):
        return self._ID

    ID = property(getID, setID)
