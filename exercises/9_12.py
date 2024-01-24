# Nutritional information per serving of M&M's:
#   Fat: 10.00 g
#   Carbohydrates: 34.00 g
#   Protein: 2.00 g
# Number of calories for 1.00 serving(s): 234.00
# Number of calories for 3.00 serving(s): 702.00
class FoodItem:
    def __init__(self, name="Water", fat=0.0, carbs=0.0, protein=0.0):
        self.name = name
        self.fat = fat
        self.carbs = carbs
        self.protein = protein

    def get_calories(self, num_servings):
        calories = ((self.fat * 9) + (self.carbs * 4) + (self.protein * 4)) * num_servings
        return calories

    def print_info(self, num_servings):
        if num_servings == 1:
            print(f'Nutritional information per serving of {self.name}:')
            print(f'  Fat: {self.fat:.2f} g')
            print(f'  Carbohydrates: {self.carbs:.2f} g')
            print(f'  Protein: {self.protein:.2f} g')
        print(f'Number of calories for {num_servings:.2f} serving(s): {self.get_calories(num_servings):.2f}')


def main():
    food_name = input()
    if food_name == "Water":
        water = FoodItem()
        water.print_info(1.00)
    else:
        fat = float(input())
        carbs = float(input())
        protein = float(input())
        servings = float(input())

        food_item = FoodItem(food_name, fat, carbs, protein)
        food_item.print_info(1.00)
        food_item.print_info(servings)

if __name__ == "__main__":
    main()
