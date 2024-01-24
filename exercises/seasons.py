import benguin

benguin.benguin()

#define valid inputs :)
valid_months = ["january", "february", "march", "april", "may", "june", "july","august", "september", "october", "november", "december"]
valid_days = [day for day in range(1, 32)]

#get user input :)
month = input("Enter the month: ").lower()
day = int(input("Enter the day: "))

#check if input is valid :)
if (month not in valid_months) or (day not in valid_days) or ((month in ["april", "june", "september", "november"]) and day == 31) or (month == "february" and (day > 29 or (day == 29))):
    print('Invalid')

#get season based on input :)
elif (month == "march" and day >= 20) or (month in ["april", "may"]) or (month == "june" and day <= 20):
    print("Spring")

elif (month == "june" and day >= 21) or (month in ["july", "august"]) or (month == "september" and day <= 21):
    print("Summer")

elif (month == "september" and day >= 22) or (month in ["october", "november"]) or (month == "december" and day <= 20):
    print("Autumn")

else:
    print("Winter")


