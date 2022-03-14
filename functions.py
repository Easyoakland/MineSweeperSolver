import pyautogui

# click top left cell
# pyautogui.click(grid[0])

# click top right cell
# pyautogui.click(grid[width-1])

# click second row on the right
# pyautogui.click(grid[(2*width)-1])


def determineLayout():
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
def identifyCell(cord, grid, width, cellwidth, cellheight, possibleCells):
    pos = convertCordToPos(cord, grid, width)
    for possibleCell in possibleCells:
        if pyautogui.locateOnScreen(possibleCell, region=(pos[0], pos[1], pos[0]+cellwidth, pos[1]+cellheight)):
            return possibleCell
        else:
            return None


def convertCordToPos(cord, grid, width):
    # offsets needed to get to each part of the cord in the grid list
    # this defines new cords have top left be 0, 0
    xOffset = cord[0]
    yOffset = width*cord[1]
    totalOffset = int(xOffset+yOffset)  # array indice must be of type int
    return grid[totalOffset]


# clicks at cell cordinate given
def click(cord, grid, width):
    pyautogui.click(convertCordToPos(cord, grid, width))


# overloaded function clicks on pos given
def clickPos(pos):
    pyautogui.click(pos)
