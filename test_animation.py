from leetcode_visualizer import process_leetcode_solution

solution = """
class Solution:
    def trap(self, height: List[int]) -> int:
        total = 0  # Initialize total water trapped
        l, r = 0, len(height) - 1  # Two pointers, left (l) and right (r)
        lmax, rmax = 0, height[r]  # Initialize max heights for left and right
        
        while l < r:
            if height[l] <= height[r]:
                # If left height is less than or equal to right height
                if height[l] < lmax:
                    total += lmax - height[l]  # Water trapped on the left
                else:
                    lmax = height[l]  # Update left max height
                l += 1  # Move left pointer
            else:
                # If right height is less than left height
                if height[r] < rmax:
                    total += rmax - height[r]  # Water trapped on the right
                else:
                    rmax = height[r]  # Update right max height
                r -= 1  # Move right pointer
        
        return total  # Return total water trapped
"""

process_leetcode_solution(solution, "rainwater_trap.mp4") 