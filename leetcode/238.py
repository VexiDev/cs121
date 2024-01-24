import benguin

benguin.benguin()

from typing import List

def productExceptSelf(nums: List[int]) -> List[int]:
    # Given an integer array nums, return an array answer such that answer[i] 
    # is equal to the product of all the elements of nums except nums[i].
    #example 
    # Input: nums = [1,2,3,4]
    # Output: [24,12,8,6]

    # left_products = {}
    # product = 1
    # for i, num in enumerate(nums):
    #     left_products[i] = product
    #     product *= num
    
    # right_product = 1
    # for i in range(len(nums)-1, -1, -1):
    #     left_products[i] *= right_product
    #     right_product *= nums[i]
    
    # return list(left_products.values())
    return [eval('*'.join(map(str, nums[:i] + nums[i+1:]))) for i in range(len(nums))]

print(productExceptSelf([1,2,3,4]))

