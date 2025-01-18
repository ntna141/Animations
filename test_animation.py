from leetcode_visualizer import process_leetcode_solution

solution = """
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        hashmap = {}
        for i in range(len(nums)):
            hashmap[nums[i]] = i
        for i in range(len(nums)):
            difference = target - nums[i]
            if difference in hashmap and hashmap[difference] != i:
                return [i, hashmap[difference]] 
"""

process_leetcode_solution(solution, "two_sum.mp4") 