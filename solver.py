# !/usr/bin/python3

"""
  Sudoku solver algorithm

  This Soduku solver uses the backtracking algorithm.

  Author: Jeroen Hamers
  Date: April 2, 2020
"""

import math


def solve(grid):
    find = find_empty(grid)
    if not find:
        return grid
    else:
        row, col = find

    for guess in range(1, len(grid)+1):
        if valid(grid, guess, (row, col)):

            # Guess a value.
            grid[row][col] = guess

            # Continue solving the grid.
            if solve(grid):
                return grid

            # If the current values do not lead to
            # success, change the value back to 0
            grid[row][col] = 0

    return False


def valid(grid, num, pos):
    # Check row.
    for i in range(len(grid[0])):
        if grid[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column.
    for i in range(len(grid)):
        if grid[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box.
    n = int(math.sqrt(len(grid)))
    box_x = pos[0] // n
    box_y = pos[1] // n

    for i in range(box_x*n, (box_x+1)*n):
        for j in range(box_y*n, (box_y+1)*n):
            if grid[i][j] == num and (i,j) != pos:
                return False

    return True


def find_empty(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 0:
                return (i, j)  # row, column

    return None


if __name__ == '__main__':

    grid = [[0,0,0,0,9,0,7,5,0],
             [0,7,0,0,0,0,9,0,4],
             [1,0,0,4,0,0,0,8,3],
             [0,0,1,5,8,0,6,0,0],
             [0,3,0,0,0,6,5,0,1],
             [6,0,9,0,0,3,0,2,0],
             [0,4,0,8,0,7,0,0,2],
             [0,0,8,0,6,0,3,0,0],
             [0,0,5,0,2,1,0,0,9]]

    solved_grid = solve(grid)
    if solved_grid:
        print(solved_grid)
    else:
        print("No solution found!")
