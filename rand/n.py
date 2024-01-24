import benguin

benguin.benguin()


#OPTIMIZED VERSION FOR LARGE VALUES n #

n = int(input("Enter a number: "))

if n < 1:
    print('\033[91m' + "Error: Number must be greater than 0" + '\033[0m')
elif n > 20:
    print(f"1+2+...+{n} = {n * (n + 1) // 2}")
else:
    total = sum(range(1, n+1))
    numbers = "+".join(str(i) for i in range(1, n+1))
    print(f"{numbers} = {total}")

# Chapter 5 complient version #
#
# n = int(input("Enter a number: "))
# total = 0
# numbers = []
# i = 1
# while i <= n:
#     total += i
#     numbers.append(str(i))
#     i += 1

# if n < 1:
#     print('\033[91m' + "Error: Number must be greater than 0" + '\033[0m')
# elif n > 20:
#     numbers = f"1+2+...+{n}"
#     print(f"{numbers} = {total}")
# else:
#     numbers = "+".join(numbers)
#     print(f"{numbers} = {total}")

