import benguin

benguin.benguin()

from typing import List

def longestConsecutive(nums: List[int]) -> int:
    nums = sorted(nums)
    longest = 0
    current = 0
    for i in range(len(nums)):
        if i == 0 or nums[i] == nums[i-1] + 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    return longest

print(longestConsecutive([100,4,200,1,3,2]))
print(longestConsecutive([0,3,7,2,5,8,4,6,0,1]))
print(longestConsecutive([0,3,7,2,5,8,4,6,0,1,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]))