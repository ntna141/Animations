from leetcode_visualizer import process_leetcode_solution

solution = """
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        node = None

        while head:
            temp = head.next
            head.next = node
            node = head
            head = temp
        
        return node 
"""

process_leetcode_solution(solution, "reverse_linkedlist.mp4") 