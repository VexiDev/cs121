import benguin

benguin.benguin()

# ask nicely for input :)
total_change = int(input('GIVE ME YOUR CHANGE: '))

#validate
if total_change <= 0:
    #naur
    print("No Change")
else:
    #math it out
    dollars = total_change // 100
    total_change = total_change % 100

    quarters = total_change // 25
    total_change = total_change % 25

    dimes = total_change // 10
    total_change = total_change % 10

    nickels = total_change // 5
    pennies = total_change % 5
    #print it out
    if dollars:
        print(f"{dollars} {'Dollar' if dollars == 1 else 'Dollars'}")
    if quarters:
        print(f"{quarters} {'Quarter' if quarters == 1 else 'Quarters'}")
    if dimes:
        print(f"{dimes} {'Dime' if dimes == 1 else 'Dimes'}")
    if nickels:
        print(f"{nickels} {'Nickel' if nickels == 1 else 'Nickels'}")
    if pennies:
        print(f"{pennies} {'Penny' if pennies == 1 else 'Pennies'}")
