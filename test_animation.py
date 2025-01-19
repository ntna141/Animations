from leetcode_visualizer import process_leetcode_solution

solution = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def maxDepth(root):
    # Base case: if root is None, return 0
    if not root:
        return 0
        
    # Recursively find the depth of left and right subtrees
    left_depth = maxDepth(root.left)
    right_depth = maxDepth(root.right)
    
    # Return the larger depth plus 1 (to count the current node)
    return max(left_depth, right_depth) + 1
"""

process_leetcode_solution(solution, "tree_max_depth.mp4") 