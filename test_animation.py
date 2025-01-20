from leetcode_visualizer import process_leetcode_solution

solution = """
# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
        # Traverse the tree
        while root:
            # If both p and q are greater than root, move right
            if p.val > root.val and q.val > root.val:
                root = root.right
            # If both p and q are less than root, move left
            elif p.val < root.val and q.val < root.val:
                root = root.left
            else:
                # We found the split point
                return root
"""

process_leetcode_solution(solution, "lowest_common_ancestor.mp4") 