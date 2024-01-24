import benguin

benguin.benguin()

print("""
Davy's auto shop services
Oil change -- $35
Tire rotation -- $19
Car wash -- $7
Car wax -- $12
""")

service_1 = input("Select first service:\n")
service_2 = input("Select second service:\n")

print("\nDavy's auto shop invoice\n")
total = 0
if service_1 == "-":
    print("Service 1: No service")

elif service_1 == "Oil change":
    print("Service 1: Oil change, $35")
    total += 35
elif service_1 == "Tire rotation":
    print("Service 1: Tire rotation, $19")
    total += 19
elif service_1 == "Car wash":
    print("Service 1: Car wash, $7")
    total += 7
elif service_1 == "Car wax":
    print("Service 1: Car wax, $12")
    total += 12
else:
    print("Invalid option")

if service_2 == "-":
    print("Service 2: No service")
elif service_2 == "Oil change":
    print("Service 2: Oil change, $35")
    total += 35
elif service_2 == "Tire rotation":
    print("Service 2: Tire rotation, $19")
    total += 19
elif service_2 == "Car wash":
    print("Service 2: Car wash, $7")
    total += 7
elif service_2 == "Car wax":
    print("Service 2: Car wax, $12")
    total += 12
else:
    print("Invalid option")

print(f"\nTotal: ${total}")