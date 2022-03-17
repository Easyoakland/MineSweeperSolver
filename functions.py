import pyautogui
from time import sleep
# click top left cell
# pyautogui.click(grid[0])

# click top right cell
# pyautogui.click(grid[width-1])

# click second row on the right
# pyautogui.click(grid[(2*width)-1])


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
        pos = self.convertCordToPos(cord)
        # testing
        # TODO remove this next line
        # pyautogui.moveTo(pos[0],pos[1])
        for i, cellTypeIm in enumerate(self.cellTypeIms):
            if pyautogui.locate(cellTypeIm, self.boardIm, region=(pos[0]-self._origin[0], pos[1]-self._origin[1], self._cellwidth, self._cellheight), grayscale=True) != None:
                return self.cellTypes[i]
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
        # only cells can update so don't bother checking if it wasn't a cell last time you checked
        if self.IDLst[self.convertCordToOffset(cord)] != "cell.png":
            return
        cell = Cell(cord, self.identifyCell2(cord))
        # if cell ID is different from recorded for that cell
        if cell.ID != self.IDLst[self.convertCordToOffset(cord)]:
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
        while a == "cell.png":
            sleep(0.05)
            self.setBoardScreenshot()
            a = self.identifyCell2(cord)
        self.updateIDLst(cord)

    # Flag tile at cord then update cell Id at location to flag
    def flag(self, cord):
        self.clickR(cord)
        self.IDLst[self.convertCordToOffset(cord)] = "flag.png"

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
