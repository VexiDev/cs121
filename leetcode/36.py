import benguin

benguin.benguin()

from typing import List
import random
import string
import time

# Set global variables for board size
BOARD_SIZE = 9
BOX_SIZE = 3

def isValidSudoku(board: List[List[str]]) -> bool:
    for row in board:
        if "".join(row).count(".") + len(set(row)) - 1 != len(row):
            return False
        
    for col in zip(*board):
        if "".join(col).count(".") + len(set(col)) - 1 != len(col):
            return False
        
    for i in range(0, BOARD_SIZE, BOX_SIZE):
        for j in range(0, BOARD_SIZE, BOX_SIZE):
            square = [board[x][y] for x in range(i, i+BOX_SIZE) for y in range(j, j+BOX_SIZE)]
            if "".join(square).count(".") + len(set(square)) - 1 != len(square):
                return False
        
    return True
            
def generate_random_sudoku():
    # generate a random uncompleted sudoku board
    return [[random.choice(string.digits) if random.random() < 0.3 else "." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def sudoku_solver(board):
    def backtrack(board, row, col):
        if col == BOARD_SIZE:
            col = 0
            row += 1
            if row == BOARD_SIZE:
                return True
        if board[row][col] != ".":
            return backtrack(board, row, col+1)
        for k in range(1, BOARD_SIZE+1):
            if isValid(board, row, col, str(k)):
                board[row][col] = str(k)
                if backtrack(board, row, col+1):
                    return True
                board[row][col] = "."
        return False

    def isValid(board, row, col, val):
        for i in range(BOARD_SIZE):
            if board[row][i] == val or board[i][col] == val:
                return False
            if board[BOX_SIZE*(row//BOX_SIZE)+i//BOX_SIZE][BOX_SIZE*(col//BOX_SIZE)+i%BOX_SIZE] == val:
                return False
        return True

    if backtrack(board, 0, 0):
        return board
    else:
        return None

valid = False
count = 1
while valid != True:
    start_time = time.time()
    sudoku = generate_random_sudoku()
    valid = isValidSudoku(sudoku)
    if valid:
        for row in sudoku:
            print(" ".join(row))
        print(f"#{count}",f"{'Valid' if valid else 'Invalid'}")
    count += 1
    end_time = time.time()


start_time2 = time.time()
result = sudoku_solver(sudoku)
end_time2 = time.time()

if result:
    print("\033[32m\nSolved Sudoku:\n")
    for row in result:
        print(" ".join(row))
    print('\033[0m')
else:
    print("\033[31mNo solution found.\033[0m")
    no_solution = True

print("Time taken to generate a valid sudoku:", round((end_time - start_time) * 1000, 4), "ms")
print("Time taken to solve the sudoku:", round((end_time2 - start_time2) * 1000, 4), "ms")
