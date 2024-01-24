import benguin

benguin.benguin()

from typing import List

def topKFrequent(nums: List[int], k: int) -> List[int]:
    # create a dictionary to store the frequency of each number
    freq = {}
    for num in nums:
        if num in freq:
            freq[num] += 1
        else:
            freq[num] = 1
    
    # sort the dictionary by frequency and return the top k numbers
    top_frequent = sorted(freq, key=freq.get, reverse=True)[:k]
    return top_frequent

print(topKFrequent([1,1,1,2,2,3], 2))
print(topKFrequent([1], 1))
print(topKFrequent([1,1,1,2,2,3,3,3,3,3,3,4,1,1,1,1,2,4,4,1,2,4,4,4,4,4,4,4,4,4,4,4,5,6,7,7,6,4,2,1,3,4,5], 2))