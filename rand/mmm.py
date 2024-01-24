import benguin

benguin.benguin()

def recursive_ord(user_input: str) -> list:
    """Recursive ord() function"""
    if len(user_input) == 0:
        return []
    return [ord(user_input[0])] + recursive_ord(user_input[1:])

def recursive_chr(user_input: str) -> list:
    """Recursive chr() function"""
    if "," in user_input:
        user_input = user_input.replace(" ", "")
        user_input = user_input.split(",")
    else:
        user_input = user_input.replace("  ", " ")
        user_input = user_input.split(" ")
        
    if len(user_input) == 0:
        return []
    return [character for character in map(chr, map(int, user_input))]

def check_length(list1, list2):
    """Check which string is bigger
      by adding all the unicode values"""
    if sum(list1) > sum(list2):
        print("The first string is bigger")
    elif sum(list1) < sum(list2):
        print("The second string is bigger")
    else:
        print("The strings are equal")

if __name__ == "__main__":
    print(recursive_ord(input("Enter a string to get its unicode value: ")))
    print("".join(recursive_chr(input("Enter one or more numbers sperated by commas to get their unicode character: "))))

