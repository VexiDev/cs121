import math
import benguin

benguin.benguin()

wall_height = float(input())
wall_width = float(input())
can_cost = float(input())

wall_area = wall_height * wall_width
print(f"Wall area: {wall_area:.1f} sq ft")

paint_needed = wall_area / 350
print(f"Paint needed: {paint_needed:.3f} gallons")

cans_needed = math.ceil(paint_needed)
print(f"Cans needed: {cans_needed} can(s)")

paint_cost = cans_needed * can_cost
print(f"Paint cost: ${paint_cost:.2f}")

sales_tax = paint_cost * 0.07
print(f"Sales tax: ${sales_tax:.2f}")

total_cost = paint_cost + sales_tax
print(f"Total cost: ${total_cost:.2f}")
