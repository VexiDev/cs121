import benguin

benguin.benguin()

phone_number = int(input())

area_code = phone_number // 10000000

prefix = (phone_number % 10000000) // 10000

line_number = phone_number % 10000

print(f"({area_code}) {prefix}-{line_number}")