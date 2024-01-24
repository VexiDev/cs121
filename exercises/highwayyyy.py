import benguin

benguin.benguin()

highway_number = int(input("Enter a highway number: "))

if not 1 <= highway_number <= 999 or (100 <= highway_number <= 199):
    print(f"{highway_number} is not a valid interstate highway number.")
else:
    if 1 <= highway_number <= 99:

        direction = "north/south" if highway_number % 2 else "east/west"
        print(f"I-{highway_number} is primary, going {direction}.")
    else:
        primary_highway_number = highway_number % 100
        if primary_highway_number == 00:
            print(f"I-{highway_number} is not a valid interstate highway number.")
        else:
            direction = "north/south" if primary_highway_number % 2 else "east/west"
            print(f"I-{highway_number} is auxiliary, servicing I-{primary_highway_number}, going {direction}.")
