import timeit
import random
import string
import benguin

benguin.benguin()

def test1(character, string):
    count = list(string).count(character)
    print(f"Test1: {count} {character}"+("'s" if count!=1 else ""))
    return 1

def test2(character, string):
    count = 0
    for char in string:
        if char == character:
            count += 1
    print(f"Test2: {count} {character}"+("'s" if count!=1 else ""))
    return 1

def generate_random_string(length):
    # Generates a random string of a given length
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_random_character():
    # Generates a single random character
    return random.choice(string.ascii_letters)

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

string_lengths = [1, 10, 100, 1000, 10000, 100000, 1000000]  # you can adjust string lengths as needed

for length in string_lengths:
    test_string = generate_random_string(length)
    test_char = generate_random_character()
    
    print(f"String length: {length}")

    wrapped = wrapper(test1, test_char, test_string)
    time1 = timeit.timeit(wrapped, number=1)

    wrapped = wrapper(test2, test_char, test_string)
    time2 = timeit.timeit(wrapped, number=1)
    
    print(f"Time for test1: {time1*1000:.6f} ms")
    print(f"Time for test2: {time2*1000:.6f} ms\n")
