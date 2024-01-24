class ItemToPurchase:
    def __init__(self, item_name='none', item_price=0, item_quantity=0, item_description='none'):
        self.item_name = item_name
        self.item_price = item_price
        self.item_quantity = item_quantity
        self.item_description = item_description

    def print_item_cost(self):
        total = self.item_price * self.item_quantity
        print(f"{self.item_name} {self.item_quantity} @ ${self.item_price} = ${total}")

    def print_item_description(self):
        print(f"{self.item_name}: {self.item_description}")


class ShoppingCart:
    def __init__(self, customer_name='none', current_date='January 1, 2016'):
        self.customer_name = customer_name
        self.current_date = current_date
        self.cart_items = []

    def add_item(self, item_to_purchase):
        self.cart_items.append(item_to_purchase)

    def remove_item(self, item_name):
        item_found = False
        for item in self.cart_items:
            if item.item_name == item_name:
                self.cart_items.remove(item)
                item_found = True
                break
        if not item_found:
            print("Item not found in cart. Nothing removed.")

    def modify_item(self, item_to_purchase):
        item_found = False
        for i in range(len(self.cart_items)):
            if self.cart_items[i].item_name == item_to_purchase.item_name:
                self.cart_items[i].item_quantity = item_to_purchase.item_quantity
                item_found = True
                break
        if not item_found:
            print("Item not found in cart. Nothing modified.")

    def get_num_items_in_cart(self):
        total_quantity = sum(item.item_quantity for item in self.cart_items)
        return total_quantity

    def get_cost_of_cart(self):
        total_cost = sum(item.item_quantity * item.item_price for item in self.cart_items)
        return total_cost

    def print_total(self):
        total_items = self.get_num_items_in_cart()
        total_cost = self.get_cost_of_cart()
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}")
        print(f"Number of Items: {total_items}\n")
        if total_items == 0:
            print("SHOPPING CART IS EMPTY")
            print("\nTotal: $0")
        else:
            for item in self.cart_items:
                item.print_item_cost()
            print("\nTotal: $" + str(total_cost))

    def print_descriptions(self):
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}\n")
        print("Item Descriptions")
        for item in self.cart_items:
            item.print_item_description()


def print_menu():
    return """
MENU
a - Add item to cart
r - Remove item from cart
c - Change item quantity
i - Output items' descriptions
o - Output shopping cart
q - Quit"""


def execute_menu(choice, cart):
    if choice == 'a':
        print("\nADD ITEM TO CART")
        item_name = input("Enter the item name:\n")
        item_desc = input("Enter the item description:\n")
        item_price = int(input("Enter the item price:\n"))
        item_quantity = int(input("Enter the item quantity:\n"))
        item_to_add = ItemToPurchase(item_name, item_price, item_quantity, item_desc)
        cart.add_item(item_to_add)

    elif choice == 'r':
        print("REMOVE ITEM FROM CART")
        item_name = input("Enter name of item to remove:\n")
        cart.remove_item(item_name)

    elif choice == 'c':
        print("CHANGE ITEM QUANTITY")
        item_name = input("Enter the item name:\n")
        quantity = int(input("Enter the new quantity:\n"))
        item_to_modify = ItemToPurchase(item_name, 0, quantity)
        cart.modify_item(item_to_modify)

    elif choice == 'i':
        print("OUTPUT ITEMS' DESCRIPTIONS")
        cart.print_descriptions()

    elif choice == 'o':
        print("OUTPUT SHOPPING CART")
        cart.print_total()


def main():
    customer_name = input("Enter customer's name:\n")
    current_date = input("Enter today's date:\n")
    print("\nCustomer name:", customer_name)
    print("Today's date:", current_date)
    cart = ShoppingCart(customer_name, current_date)

    print(print_menu())
    choice = input("\nChoose an option:\n")
    while choice != 'q':
        while choice not in ['a', 'r', 'c', 'i', 'o', 'q']:
            choice = input("Choose an option:\n")
        if choice == 'q':
            break
        execute_menu(choice, cart)
        print(print_menu())
        choice = input("\nChoose an option:\n")


if __name__ == "__main__":
    main()
