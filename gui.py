# !/usr/bin/python3

"""
  Sudoku Graphical User Interface

  user interaction:
    - Left Mouse Button: select cells
    - K_1 to K_9       : add/delete selected cell values in sketch mode
                         add/change selected cell value in normal mode
    - K_DEL            : delete selected cell value in normal mode
    - K_SPACE          : turn on/off sketch functionality
    - K_RETURN         : check the values
                         green background: correct
                         red background: fault
    - K_n              : start new game

  Author: Jeroen Hamers
  Date: April 3, 2020
"""

import os
import sys
import random
import pygame
import copy
import solver
import math

pygame.font.init()

# Makes sure that the pygame window will be placed at
# the center of the screen.
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Constant definitions.
CELLSIZE = 60
DIM_ROW = 9
DIM_CELL = 3

GLOBAL_FONT = pygame.font.SysFont('comicsans', 40)
LOCAL_FONT = pygame.font.SysFont('comicsans', 20)

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(150, 0, 0)
GREEN = pygame.Color(0, 150, 0)
BLUE = pygame.Color(0, 0, 255)
GREY_SEL = pygame.Color(200, 200, 200)
GREY_SKETCH = pygame.Color(130, 130, 130)

# The file path to a document containing 1 million
# different Sudoku grids. Each line consists of a
# string of 81 characters.
FPATH = os.path.join(
    os.path.abspath(os.path.dirname(sys.argv[0])),
    "sudoku.csv"
)


# Lambda functions.
f1 = lambda row, col: row * DIM_ROW + col
f2 = lambda idx: (math.floor(idx / DIM_ROW), idx % DIM_ROW)
f3 = lambda mainlist: [item for sublist in mainlist for item in sublist]


# Read in the Sudoku grids and use a pseudo-random
# generator to select one.
def get_soduku_grid():
    with open(FPATH, 'r') as fid:
        rows = fid.readlines()
        row = rows[random.randint(0, len(rows))].strip()

    return [int(i) for i in row]


class Sudoku:

    def __init__(self, nScreenWidth, nScreenHeight, grid):

        # Set window properties.
        self.window = pygame.display.set_mode((nScreenWidth, nScreenHeight))
        self.nScreenWidth = nScreenWidth
        self.nScreenHeight = nScreenHeight
        self.cells = self.create_cells(grid)

        # Set initial selected cell.
        self.nCurrentSelectedCellX, self.nCurrentSelectedCellY = \
            f2(grid.index(0))

        # Set text properties
        self.xshift = 7
        self.yshift = 9

        # Set boolean properties.
        self.bSketchOn = False
        self.bShowSolution = False

    def create_cells(self, grid):
        # solve the sudoku and return the solved grid
        sgrid = f3(solver.main(grid, DIM_ROW))

        # create the individual grid cells
        cells = []
        for i in range(len(grid)):
            x, y = f2(i)
            cells.append(Cell(x * CELLSIZE, y * CELLSIZE, grid[i], sgrid[i]))

        return cells


    # Draw the Sudoku grid.
    def draw_grid(self):

        # Draw a border around the selected square.
        self.draw_border_selection()

        # Loop through all grid cells.
        for cell in self.cells:
            xglob, yglob = cell.global_coors
            xglob_text = xglob + CELLSIZE // 2 - self.xshift
            yglob_text = yglob + CELLSIZE // 2 - self.yshift

            local = cell.local_coors

            ivalue = cell.init_value
            uvalue = cell.user_value
            svalue = cell.solved_value

            # Display initial cell values
            if ivalue > 0:
                self.display_numbers(
                    xglob_text, yglob_text, ivalue, GLOBAL_FONT, BLACK)

            # Check if the "normal", "sketch" or "solution"
            # mode is toggled.
            if self.bShowSolution:
                color_user = WHITE

                # Only check user input values.
                if uvalue > 0:
                    if uvalue == svalue:
                        bcolor = GREEN
                        color_sketch = GREEN
                    else:
                        bcolor = RED
                        color_sketch = RED

                    if uvalue > ivalue:
                        pygame.draw.rect(
                            self.window, bcolor,
                            (xglob, yglob, CELLSIZE, CELLSIZE))

            elif self.bSketchOn:
                color_user = GREY_SKETCH
                color_sketch = BLUE
            else:
                color_user = BLUE
                color_sketch = GREY_SKETCH

            # Change the layer order when "sketch" mode
            # is turned on/off to optimize display.
            if self.bSketchOn:

                # Only check user input values.
                if uvalue > ivalue:
                    self.display_numbers(
                        xglob_text, yglob_text, uvalue,
                        GLOBAL_FONT, color_user)

                for i in range(len(local)):
                    if cell.sketch_values[i]:
                        self.display_numbers(
                            local[i][0], local[i][1],
                            i+1, LOCAL_FONT, color_sketch)

            else:
                for i in range(len(local)):
                    if cell.sketch_values[i]:
                        self.display_numbers(
                            local[i][0], local[i][1],
                            i+1, LOCAL_FONT, color_sketch)

                # Only check user input values.
                if uvalue > ivalue:
                    self.display_numbers(
                        xglob_text, yglob_text, uvalue,
                        GLOBAL_FONT, color_user)

        # Draw a border around the grid.
        pygame.draw.rect(self.window, BLACK, self.window.get_rect(), 3)

        # Draw lines to create the individual cells.
        for i in range(1, DIM_ROW):
            width = 1
            if i % DIM_CELL == 0:
                width = 3

            # Draw vertical lines.
            pygame.draw.line(
                self.window, BLACK,
                (i * CELLSIZE, 0),
                (i * CELLSIZE, self.nScreenHeight), width)

            # Draw horizontal lines.
            pygame.draw.line(
                self.window, BLACK,
                (0, i * CELLSIZE),
                (self.nScreenWidth, i * CELLSIZE), width)

    # Draw a border around the selected square.
    def draw_border_selection(self):
        x = self.nCurrentSelectedCellX * CELLSIZE
        y = self.nCurrentSelectedCellY * CELLSIZE

        pygame.draw.rect(self.window, GREY_SEL, (x, y, CELLSIZE, CELLSIZE))

    # Display the numbers.
    def display_numbers(self, x, y, value, font, color):
        self.window.blit(font.render(f"{value}", True, color), (x, y))


class Cell:

    def __init__(self, xpos, ypos, value, svalue):

        # Set text properties
        self.xshift = 7
        self.yshift = 5

        # Set global and local cell coordinates
        self.global_coors = (xpos, ypos)
        self.local_coors = self.set_local_coors(xpos, ypos)

        self.init_value = value
        self.user_value = value
        self.solved_value = svalue
        self.sketch_values = [False] * 9

        # Set boolean properties.
        self.bCanModifyValue = True if value == 0 else False
        self.bCorrectValueFound = False

    def set_local_coors(self, xglob, yglob):
        local = []

        for i in range(DIM_CELL):
            for j in range(DIM_CELL):
                local.append((
                    xglob + j*(CELLSIZE // 3) + self.xshift,
                    yglob + i*(CELLSIZE // 3) + self.yshift
                ))

        return local

# Main loop.
def main(width, height, grid):

    # Initialize the Sudoku grid.
    sudoku = Sudoku(width, height, grid)

    # Run until closed by the user.
    flag = True
    while flag:

        # Set the window background color.
        sudoku.window.fill(WHITE)

        # Event handling.

        # Select the cell based on the current location of
        # the mouse cursor.
        nMouseX, nMouseY = pygame.mouse.get_pos()
        nSelectedCellX = nMouseX // CELLSIZE
        nSelectedCellY = nMouseY // CELLSIZE

        cell = sudoku.cells[
            f1(sudoku.nCurrentSelectedCellX, sudoku.nCurrentSelectedCellY)]

        # Loop through all events
        for event in pygame.event.get():

            # Check if a key is pressed.
            if event.type == pygame.KEYDOWN:

                # If the space bar is pressed toggle the display
                # of the sketche d grid on or off.
                if event.key == pygame.K_SPACE:
                    sudoku.bSketchOn = not sudoku.bSketchOn
                    sudoku.bShowSolution = False

                # Display the numbers the user typed in and store
                # them in the grid.
                elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    if sudoku.bSketchOn:
                        cell.sketch_values[0] = not cell.sketch_values[0]
                    else:
                        cell.user_value = 1

                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    if sudoku.bSketchOn:
                        cell.sketch_values[1] = not cell.sketch_values[1]
                    else:
                        cell.user_value = 2

                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    if sudoku.bSketchOn:
                        cell.sketch_values[2] = not cell.sketch_values[2]
                    else:
                        cell.user_value = 3

                elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                    if sudoku.bSketchOn:
                        cell.sketch_values[3] = not cell.sketch_values[3]
                    else:
                        cell.user_value = 4

                elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                    if sudoku.bSketchOn:
                        cell.sketch_values[4] = not cell.sketch_values[4]
                    else:
                        cell.user_value = 5

                elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                    if sudoku.bSketchOn:
                        cell.sketch_values[5] = not cell.sketch_values[5]
                    else:
                        cell.user_value = 6

                elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                    if sudoku.bSketchOn:
                        cell.sketch_values[6] = not cell.sketch_values[6]
                    else:
                        cell.user_value = 7

                elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                    if sudoku.bSketchOn:
                        cell.sketch_values[7] = not cell.sketch_values[7]
                    else:
                        cell.user_value = 8

                elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                    if sudoku.bSketchOn:
                        cell.sketch_values[8] = not cell.sketch_values[8]
                    else:
                        cell.user_value = 9

                # Delete the value of the current selected cell.
                elif event.key == pygame.K_DELETE:
                    cell.user_value = 0

                # Show solution values.
                elif event.key == pygame.K_RETURN:
                    if not sudoku.bSketchOn:
                        sudoku.bShowSolution = not sudoku.bShowSolution

                # Start a new game.
                elif event.key == pygame.K_n:
                    del sudoku
                    sudoku = Sudoku(540, 540, get_soduku_grid())

            # Toggle the display of a border around the selected
            # cell on or off.
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                new_cell = sudoku.cells[f1(nSelectedCellX, nSelectedCellY)]
                if new_cell.init_value == 0:
                    sudoku.nCurrentSelectedCellX = nSelectedCellX
                    sudoku.nCurrentSelectedCellY = nSelectedCellY

            # Quit the loop when the user has pressed the "x" button.
            elif event.type == pygame.QUIT:
                flag = False

        # Redraw the grid.
        sudoku.draw_grid()

        # Update the window.
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Sudoku Game')

    main(540, 540, get_soduku_grid())

    pygame.quit()
