from typing import Optional

class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: Optional['Node'] = None 
        
    def __str__(self) -> str:
        return str(self.value) 

class TreeNode:
    def __init__(self, value: int):
        self.value = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        
    def __str__(self) -> str:
        return str(self.value) 