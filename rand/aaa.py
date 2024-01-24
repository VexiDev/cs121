import benguin

benguin.benguin()

numbers = [5, 1, -7, -2, -1, -9]
for position, number in enumerate(numbers):
    if number < 0:
        print(f'{position} x')
    else:
        print(f'{position} {number}')