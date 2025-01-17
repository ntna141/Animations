from leetcode_visualizer import process_leetcode_solution

def test_merge_sort():
    solution = """
def mergeSort(self, arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left = self.mergeSort(arr[:mid])
    right = self.mergeSort(arr[mid:])
    
    
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
"""
    
    process_leetcode_solution(solution, "merge_sort.mp4")

if __name__ == "__main__":
    test_merge_sort() 