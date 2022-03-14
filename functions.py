import pyautogui

# click top left cell
# pyautogui.click(grid[0])

# click top right cell
# pyautogui.click(grid[width-1])

# click second row on the right
# pyautogui.click(grid[(2*width)-1])


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

        # set the width and height of the game in cells based upon the width of each cell and the size of the board
        width = ((end[0]+cellwidth)-origin[0])/cellwidth
        height = ((end[1]+cellheight)-origin[1])/cellheight

        return width, height, cellwidth, cellheight, origin, end, grid

    # iterates through all possible images to see if one matches
    # if the image matches the if statement will be true and the image's string will be returned
    def identifyCell(self, cord, possibleCells):
        pos = self.convertCordToPos(cord)
        for possibleCell in possibleCells:
            if pyautogui.locateOnScreen(possibleCell, region=(pos[0], pos[1], self._cellwidth, self._cellheight))!=None:
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

    # clicks at cell cordinate given
    def click(self, cord):
        pyautogui.click(self.convertCordToPos(cord))

    # click on pos given
    def clickPos(self, pos):
        pyautogui.click(pos)

    # possibleCells setter
    def setPossibleCells(self, possibleCells):
        self._possibleCells = possibleCells

    # possibleCells getter
    def getPossibleCells(self):
        return self._possibleCells

    possibleCells = property(getPossibleCells, setPossibleCells)
