from leetcode_visualizer import process_leetcode_solution

solution = """
def threeSum(self, nums):
    nums.sort()  # Sort array first
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicates for i
        if i > 0 and nums[i] == nums[i-1]:
            continue
            
        left = i + 1
        right = len(nums) - 1
        
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            
            if current_sum == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for left
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for right
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
                
    return result
"""

process_leetcode_solution(solution, "three_sum.mp4") 