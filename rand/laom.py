import benguin

benguin.benguin()


num1, num2 = int(input('Enter a number: ')), int(input('Enter another number: '))

if num1 > num2:
    print(f'{num1} is greater than {num2}')
elif num1 < num2:
    print(f'{num1} is less than {num2}')
else:
    print(f'{num1} is equal to {num2}')