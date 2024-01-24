import benguin

benguin.benguin()

def isPalindrome(s: str) -> bool:
    formated_s = ''.join(character for character in s if character.isalnum()).lower()
    return formated_s == formated_s[::-1]


print(isPalindrome("race a car"))
print(isPalindrome("A man, a plan, a canal: Panama"))