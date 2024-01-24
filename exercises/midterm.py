character = input()
while character != 'quit':    
    count = list(input()).count(character)
    print(f"{count} {character}"+("'s" if count!=1 else ""))
    character = input()

# Part 1. Write a program whose input is a character and a string, and whose 
# output indicates the number of times the character appears in the string. 
# The output should include the input character and use the plural form, n's,
# if the number of times the characters appears is not exactly 1. (30 pts)

# Part 2. Modify the program so the user can try the above
# multiple times until the user decides to quit. Use 'quit'
# as the sentinel value to terminate the program. (10 pts.)  