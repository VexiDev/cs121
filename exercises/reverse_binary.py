
import benguin

benguin.benguin()

x = int(input())
reverse_binary = ""
while x > 0:
    reverse_binary += str(x % 2) 
    x //= 2
print(reverse_binary)
