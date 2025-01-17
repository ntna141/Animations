from leetcode_visualizer import process_leetcode_solution

solution = """
def twoSum(self, nums, target):
    seen = {}  # value -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in seen:
            return [seen[complement], i]
            
        seen[num] = i
    
    return []  # No solution found
"""

process_leetcode_solution(solution, "two_sum.mp4") 