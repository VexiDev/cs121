import benguin
import math

benguin.benguin()

class Car:
    def __init__(self):
        self.MPG = 0
        self.gas_gallon = 0

    def print_car(self):
        print(f"The MPG of the car is {self.MPG}, and the gas left in the gas tank is {self.gas_gallon} gallons.")

    def add_gas(self, gas):
        self.gas_gallon += gas

    def drive(self, miles):
        required_gas = math.ceil(miles / self.MPG)
        if required_gas > self.gas_gallon:
            additional_gas_needed = required_gas - self.gas_gallon
            print(f"There is not enough gas left to drive {miles} miles. You need to add at least {additional_gas_needed} more gallons.")
        else:
            self.gas_gallon -= required_gas

if __name__ == '__main__':
    car = Car()
    car.MPG = int(input("Enter the MPG of the car:\n"))
    car.gas_gallon = int(input("Enter the gallons of gas in the tank:\n"))
    additional_gas = int(input("Enter the gallons of gas to add:\n"))
    car.add_gas(additional_gas)
    miles_to_drive = int(input("Enter the miles to drive:\n"))
    car.drive(miles_to_drive)
    car.print_car()

    while True:
        action = input("Enter A to add gas, enter D to drive, and enter Q to quit:\n").upper()
        if action == 'Q':
            break
        elif action == 'A':
            additional_gas = int(input("Enter the gallons of gas to add:\n"))
            car.add_gas(additional_gas)
        elif action == 'D':
            miles_to_drive = int(input("Enter the miles to drive:\n"))
            car.drive(miles_to_drive)
            car.print_car()
