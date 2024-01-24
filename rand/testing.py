import benguin

benguin.benguin()

t = "anagram"
s = "nagaram"

def isAnagram(s: str, t: str) -> bool:
    #convert strings to lists
    s_list, t_list = list(s), list(t)
    #sort lists
    s_list.sort()
    t_list.sort()
    #compare sorted string lists
    return t_list == s_list

print(isAnagram(s, t))