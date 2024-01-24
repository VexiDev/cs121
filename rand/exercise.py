import benguin

benguin.benguin()

value = input("\nEnter a value or 'q' to quit: ")

sum = 0
count = 0
while value != "q":
    try:
        sum += int(value)
        count += 1
        value = input("Enter a value or 'q' to quit: ")
    except ValueError:
        print(f'\033[3;91mError: Invalid input \033[0m')
        value = input("Enter a value or 'q' to quit: ")

try:
    print(f'\n\033[32mThe sum of the values is {sum}, and the average is {sum/count:.2f}\n\033[0m')
except ZeroDivisionError:
    print(f'\033[1;91mError: Zero Division \033[0m')