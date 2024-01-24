import math
import benguin

benguin.benguin()

# These problems are not sorted in any particular order just whenever I feel like testing the code.

# 2.22
def test_1():
    radius1 = float(input('Enter the radius of the first circle'))
    radius2 = float(input('Enter the radius of the second circle'))

    print(f'The area of the second circle is {math.pi * radius2 ** 2}')
    print(f'The area of the first circle is {math.pi * radius1 ** 2}')
    print(f'The ratio between the two areas is {math.pi * radius1 ** 2 / math.pi * radius2 ** 2}')

# 2.7
def test_2():
    amount_to_change = int(input())

    num_fives = amount_to_change // 5

    num_ones = amount_to_change % 5

    print('Change for $', amount_to_change)
    print(num_fives, '$5 bill(s) and', num_ones, '$1 bill(s)')

# 2.8
def test_3():
    avg_sales = 0

    num_sales1 = int(input())
    num_sales2 = int(input())
    num_sales3 = int(input())

    avg_sales = (num_sales1 + num_sales2 + num_sales3) / 3

    print(f'Average sales: {avg_sales:.2f}')

# 2.8.2
def test_4():
    pi = 3.14159
    sphere_volume = 0.0

    sphere_radius = float(input())

    sphere_volume = (4 / 3) * pi * sphere_radius ** 3

    print(f'Sphere volume: {sphere_volume:.2f}')

# 2.8.3
def test_5():
    G = 6.673e-11
    M = 5.98e24
    accel_gravity = 0.0

    dist_center = float(input())

    accel_gravity = (G * M) / dist_center ** 2

    print(f'Acceleration of gravity: {accel_gravity:.2f}')

