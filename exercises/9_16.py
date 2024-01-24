class ItemToPurchase:
    def __init__(self):
        self.item_name = "none"
        self.item_price = 0
        self.item_quantity = 0
        self.item_description = "none"

    def print_item_cost(self):
        total_cost = self.item_price * self.item_quantity
        print(f'{self.item_name} {self.item_quantity} @ ${self.item_price} = ${total_cost}')

    def print_item_description(self):
        print(f'{self.item_name}: {self.item_description}')

class ShoppingCart:
    def __init__(self, customer_name="none", current_date="January 1, 2016"):
        self.customer_name = customer_name
        self.current_date = current_date
        self.cart_items = []

    def add_item(self, ItemToPurchase):
        self.cart_items.append(ItemToPurchase)

    def remove_item(self, item_name):
        item_found = False
        for item in self.cart_items:
            if item.item_name == item_name:
                self.cart_items.remove(item)
                item_found = True
                break
        if not item_found:
            print("Item not found in cart. Nothing removed.\n")

    def modify_item(self, ItemToPurchase):
        item_found = False
        for i in range(len(self.cart_items)):
            if self.cart_items[i].item_name == ItemToPurchase.item_name:
                self.cart_items[i].item_quantity = ItemToPurchase.item_quantity
                item_found = True
                break
        if not item_found:
            print("Item not found in cart. Nothing modified.\n")

    def get_num_items_in_cart(self):
        total_quantity = sum(item.item_quantity for item in self.cart_items)
        return total_quantity

    def get_cost_of_cart(self):
        total_cost = sum(item.item_price * item.item_quantity for item in self.cart_items)
        return total_cost

    def print_total(self):
        total_cost = self.get_cost_of_cart()
        print(f"\nOUTPUT SHOPPING CART")
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}")
        print(f"Number of Items: {self.get_num_items_in_cart()}\n")
        if total_cost == 0:
            print("SHOPPING CART IS EMPTY\n")
            print(f"Total: ${total_cost}\n")
        else:
            for item in self.cart_items:
                item.print_item_cost()
            print(f"\nTotal: ${total_cost}\n")

    def print_descriptions(self):
        print(f"\nOUTPUT ITEMS' DESCRIPTIONS")
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}\n")
        print("Item Descriptions")
        if len(self.cart_items) == 0:
            print("SHOPPING CART IS EMPTY\n")
        else:
            for item in self.cart_items:
                item.print_item_description()
            print()


def print_menu():
    menu = (
        "\nMENU\n"
        "a - Add item to cart\n"
        "r - Remove item from cart\n"
        "c - Change item quantity\n"
        "i - Output items' descriptions\n"
        "o - Output shopping cart\n"
        "q - Quit\n"
    )
    print(menu)

def execute_menu(choice, cart):
    if choice == 'a':
        print("\nADD ITEM TO CART")
        item_name = input("Enter the item name:\n")
        item_desc = input("Enter the item description:\n")
        item_price = int(input("Enter the item price:\n"))
        item_quant = int(input("Enter the item quantity:\n"))

        new_item = ItemToPurchase()
        new_item.item_name = item_name
        new_item.item_description = item_desc
        new_item.item_price = item_price
        new_item.item_quantity = item_quant

        cart.add_item(new_item)
        print()

    elif choice == 'r':
        print("\nREMOVE ITEM FROM CART")
        item_name = input("Enter name of item to remove:\n")
        cart.remove_item(item_name)

    elif choice == 'c':
        print("\nCHANGE ITEM QUANTITY")
        item_name = input("Enter the item name:\n")
        quantity = int(input("Enter the new quantity:\n"))

        new_item = ItemToPurchase()
        new_item.item_name = item_name
        new_item.item_quantity = quantity

        cart.modify_item(new_item)

    elif choice == 'i':
        cart.print_descriptions()

    elif choice == 'o':
        cart.print_total()

    elif choice == 'q':
        return

def main():
    customer_name = input("Enter customer's name:\n")
    current_date = input("Enter today's date:\n")
    print("\nCustomer name:", customer_name)
    print("Today's date:", current_date)

    cart = ShoppingCart(customer_name, current_date)

    choice = ''
    while choice != 'q':
        print_menu()
        choice = input("Choose an option:\n").lower()
        execute_menu(choice, cart)

if __name__ == "__main__":
    main()
