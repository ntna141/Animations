from typing import Optional

class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: Optional['Node'] = None 