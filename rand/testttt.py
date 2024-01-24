class Employee:
    def __init__(self, name='unknown', wage=0.0, hours=0.0):
        self.name = name
        self.wage = wage
        self.hours = hours

emp1 = Employee()
print(emp1.name, emp1.wage, emp1.hours)

emp2 = Employee("John Doe", 15.0, 40.0)
print(emp2.name, emp2.wage, emp2.hours)