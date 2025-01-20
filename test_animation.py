from leetcode_visualizer import process_leetcode_solution

solution = """
class Solution:
    def canJump(self, nums: List[int]) -> bool:
        goal = len(nums) - 1

        for i in range(len(nums) - 2, -1, -1):
            if i + nums[i] >= goal:
                goal = i
        
        return True if goal == 0 else False
"""

process_leetcode_solution(solution, "jump_game.mp4") 