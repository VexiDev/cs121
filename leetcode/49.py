import benguin

benguin.benguin()

from typing import List

def groupAnagrams(strs: List[str]) -> List[List[str]]:
    output = []
    for word in strs:
        for anagram in output:
            if sorted(word) == sorted(anagram[0]):
                anagram.append(word)
                break
        else:
            output.append([word])

    return output[::-1]

print(groupAnagrams(["eat","tea","tan","ate","nat","bat"]))
print(groupAnagrams(["listen", "silent", "elbow", "below", "state", "taste", "night", "thing", "act", "cat", "tac"]))
print(groupAnagrams([""]))
print(groupAnagrams(["a"]))