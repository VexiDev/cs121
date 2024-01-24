import benguin
import unittest

benguin.benguin()

def num_to_letter_grade(grade):
    if grade >= 90:
        return "A"
    elif grade >= 80:
        return "B"
    elif grade >= 70:
        return "C"
    elif grade >= 60:
        return "D"
    else:
        return "F"

class TestNumToLetterGrade(unittest.TestCase):

    def test_A_grade(self):
        self.assertEqual(num_to_letter_grade(95), "A")
        self.assertEqual(num_to_letter_grade(90), "A")

    def test_B_grade(self):
        self.assertEqual(num_to_letter_grade(85), "B")
        self.assertEqual(num_to_letter_grade(80), "B")

    def test_C_grade(self):
        self.assertEqual(num_to_letter_grade(75), "C")
        self.assertEqual(num_to_letter_grade(70), "C")

    def test_D_grade(self):
        self.assertEqual(num_to_letter_grade(65), "D")
        self.assertEqual(num_to_letter_grade(60), "D")

    def test_F_grade(self):
        self.assertEqual(num_to_letter_grade(59), "F")
        self.assertEqual(num_to_letter_grade(0), "F")

print(num_to_letter_grade(int(input("Enter a grade: "))))

if __name__ == '__main__':
    unittest.main()








#better way 
# grade = int(input("Enter a grade: "))
# grades = {90: "A", 80: "B", 70: "C", 60: "D", 0: "F"}
# letter_grade = next((grade_letter for grade_cutoff, grade_letter in grades.items() if grade >= grade_cutoff), "F")
# print(letter_grade)