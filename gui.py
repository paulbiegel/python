# !/usr/bin/python3

"""
  Sudoku Graphical User Interface

  user interaction:
    - Left Mouse Button: select squares
    - K_1 to K_9       : type in values
    - Space Bar        : check values
                         green background: correct value
                         red background: incorrect value
    - K_DEL            : delete value from selected square
    - K_n              : start new game

  Author: Jeroen Hamers
  Date: April 2, 2020
"""

import os
import sys
import random
import pygame
import copy
import solver
import math

# Makes sure that the pygame window will be placed at
# the center of the screen.
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Constant definitions.
pygame.font.init()
FONT = pygame.font.SysFont('comicsans', 40)
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 150, 0)
BLUE = pygame.Color(0, 0, 255)
GREY = pygame.Color(200, 200, 200)

# The file path to a document containing 1 million
# different Sudoku grids. Each line consists of a
# string of 81 characters.
FPATH = os.path.join(
    os.path.abspath(os.path.dirname(sys.argv[0])),
    "sudoku.csv"
)


# Flatten a 2D list into 1D
flatten = lambda mainlist: [item for sublist in mainlist for item in sublist]


# Read in the Sudoku grids and use a pseudo-random
# generator to select one.
def get_soduku_grid():
    with open(FPATH, 'r') as fid:
        rows = fid.readlines()
        row = rows[random.randint(0, len(rows))].strip()
        row = [int(i) for i in row]

    nSquare = round(math.sqrt(len(row)))

    grid = []
    for i in range(0, len(row), nSquare):
        grid.append(row[i:i+nSquare])

    return grid


# This class generates and draws the Sudoku grid on the screen.
class Grid:

    def __init__(self, nScreenWidth, nScreenHeight, grid):

        # Set window properties.
        self.window = pygame.display.set_mode((nScreenWidth, nScreenHeight))
        self.nScreenWidth = nScreenWidth
        self.nScreenHeight = nScreenHeight
        self.nSquare = len(grid)
        self.nCellSize = self.nScreenWidth // self.nSquare

        # Set initial selected square.
        idx = [i for i in range(len(flatten(grid))) if flatten(grid)[i] == 0]
        self.nCurrentSelectedCellX = idx[0] % self.nSquare
        self.nCurrentSelectedCellY = math.floor(idx[0] / self.nSquare)

        # Set text properties.
        self.xshift = 7
        self.yshift = 9
        self.solved_color = WHITE
        self.user_color = WHITE

        # Set boolean properties.
        self.bShowSolution = False  # show the solved Soduku

        # Set solver properties.
        self.init_grid = copy.deepcopy(grid)
        self.user_grid = copy.deepcopy(grid)
        self.solved_grid = solver.solve(grid)
        self.nCountCorrect = len([i for i in flatten(self.init_grid) if i > 0])

    # Draw the grid.
    def draw_grid(self):

        # Draw a border around the selected square.
        self.draw_border_selection()

        # Check the solution and show incorrect values.
        if self.bShowSolution:
            self.user_color = WHITE
            self.check_solution()
        else:
            self.user_color = BLUE

        # Draw a border around the grid.
        pygame.draw.rect(self.window, BLACK, self.window.get_rect(), 3)

        # Draw lines to create the individual squares.
        n = math.sqrt(self.nSquare)
        for i in range(1, self.nSquare):
            width = 1
            if i % n == 0:
                width = 3

            # Draw vertical lines.
            pygame.draw.line(
                self.window, BLACK,
                (i * self.nCellSize, 0),
                (i * self.nCellSize, self.nScreenHeight), width)

            # Draw horizontal lines.
            pygame.draw.line(
                self.window, BLACK,
                (0, i * self.nCellSize),
                (self.nScreenWidth, i * self.nCellSize), width)

        # Draw the initial grid, the user grid and the solved grid.
        for i in range(0, self.nSquare):
            for j in range(0, self.nSquare):

                # Select the square values.
                ivalue = self.init_grid[j][i]    # initial grid value
                uvalue = self.user_grid[j][i]    # user grid value
                svalue = self.solved_grid[j][i]  # solved grid value

                # Only display initial grid values larger than zeros.
                # A zero resembles an empty square.
                if ivalue > 0:

                    text_init_grid = FONT.render(f"{ivalue}", True, BLACK)

                    self.window.blit(text_init_grid,
                        (i * self.nCellSize +
                            self.nCellSize // 2 - self.xshift,
                         j * self.nCellSize +
                            self.nCellSize // 2 - self.yshift))

                else:

                    # Check if the user typed in a value, if so display it.
                    if uvalue > ivalue:

                        text_user_grid = FONT.render(
                            f"{uvalue}", True, self.user_color)

                        self.window.blit(text_user_grid,
                            (i * self.nCellSize +
                                self.nCellSize // 2 - self.xshift,
                             j * self.nCellSize +
                                self.nCellSize // 2 - self.yshift))

    # Draw a border around the selected square.
    def draw_border_selection(self):
        x = self.nCurrentSelectedCellX * self.nCellSize
        y = self.nCurrentSelectedCellY * self.nCellSize

        pygame.draw.rect(self.window, GREY,
            (x, y, self.nCellSize, self.nCellSize))

    # Draw a border around the checked square.
    def draw_border_check(self, sx, sy, bordercolor):
        x = sx * self.nCellSize
        y = sy * self.nCellSize

        pygame.draw.rect(self.window, bordercolor,
            (x, y, self.nCellSize, self.nCellSize))

    # Check if the typed in numbers are correct.
    def check_solution(self):
        user_values = flatten(self.user_grid)
        solved_values = flatten(self.solved_grid)
        init_values = flatten(self.init_grid)

        # Check for correct values.
        correctIdx = [
            i for i in range(len(user_values)) if
            user_values[i] == solved_values[i] and user_values[i]>0
            and user_values[i] != init_values[i]
        ]

        # Draw a green border around the squares that contain
        # a correct value
        for idx in correctIdx:
            self.draw_border_check(
                idx % self.nSquare, math.floor(idx / self.nSquare), GREEN
            )

        # Check for incorrect values.
        incorrectIdx = [
            i for i in range(len(user_values)) if
            user_values[i] != solved_values[i] and user_values[i]>0
        ]

        # Draw a red border around the squares that contain
        # an incorrect value
        for idx in incorrectIdx:
            self.draw_border_check(
                idx % self.nSquare, math.floor(idx / self.nSquare), RED
            )

# Main loop.
def main(width, height, grid):

    # Initialize the Sudoku grid.
    grid = Grid(width, height, grid)

    # Run until closed by the user.
    flag = True
    while flag:

        # Set the window background color.
        grid.window.fill((255, 255, 255))

        # Event handling.

        # Define the square based on the current location of
        # the mouse cursor.
        nMouseX, nMouseY = pygame.mouse.get_pos()
        nSelectedCellX = nMouseX // grid.nCellSize
        nSelectedCellY = nMouseY // grid.nCellSize

        ncx = grid.nCurrentSelectedCellX
        ncy = grid.nCurrentSelectedCellY

        # Loop through all events
        for event in pygame.event.get():

            # Check if a key is pressed.
            if event.type == pygame.KEYDOWN:
                grid.user_color = BLUE

                # If the space bar is pressed toggle the display
                # of the solved grid on or off.
                if event.key == pygame.K_SPACE:
                    grid.bShowSolution = not grid.bShowSolution

                # If the "n" key is pressed, load a new grid and
                # reset all the variables.
                elif event.key == pygame.K_n:
                    grid.bShowSolution = False
                    grid.solved_color = WHITE
                    grid.user_color = WHITE

                    # Load a new random Sudoku grid.
                    new_grid = get_soduku_grid()

                    idx = [i for i in range(len(flatten(new_grid))) if \
                        flatten(new_grid)[i] == 0]
                    grid.nCurrentSelectedCellX = idx[0] % grid.nSquare
                    grid.nCurrentSelectedCellY = math.floor(
                        idx[0] / grid.nSquare)

                    # Reset all the grid.
                    grid.init_grid = copy.deepcopy(new_grid)
                    grid.user_grid = copy.deepcopy(new_grid)
                    grid.solved_grid = copy.deepcopy(solver.solve(new_grid))

                # Display the numbers the user typed in and store
                # them in the grid.
                elif event.key == pygame.K_1:
                    grid.user_grid[ncy][ncx] = 1
                elif event.key == pygame.K_2:
                    grid.user_grid[ncy][ncx] = 2
                elif event.key == pygame.K_3:
                    grid.user_grid[ncy][ncx] = 3
                elif event.key == pygame.K_4:
                    grid.user_grid[ncy][ncx] = 4
                elif event.key == pygame.K_5:
                    grid.user_grid[ncy][ncx] = 5
                elif event.key == pygame.K_6:
                    grid.user_grid[ncy][ncx] = 6
                elif event.key == pygame.K_7:
                    grid.user_grid[ncy][ncx] = 7
                elif event.key == pygame.K_8:
                    grid.user_grid[ncy][ncx] = 8
                elif event.key == pygame.K_9:
                    grid.user_grid[ncy][ncx] = 9

                # Delete the value of the current selected square
                elif event.key == pygame.K_DELETE:
                    grid.user_grid[nSelectedCellY][nSelectedCellX] = 0

            # Toggle the display of a border around the selected
            # square on or off.
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if grid.init_grid[nSelectedCellY][nSelectedCellX] == 0:
                    grid.nCurrentSelectedCellX = nSelectedCellX
                    grid.nCurrentSelectedCellY = nSelectedCellY

            # Quit the loop when the user has pressed the "x" button.
            if event.type == pygame.QUIT:
                flag = False

        # Redraw the grid.
        grid.draw_grid()

        # Update the window.
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Sudoku Game')

    main(540, 540, get_soduku_grid())

    pygame.quit()
