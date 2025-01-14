from linked_list_visualizer import LinkedListVisualizer, Node
import os
import glob

if __name__ == "__main__":
    # Clean up any existing frames
    for f in glob.glob("frames/*.png"):
        os.remove(f)
    
    visualizer = LinkedListVisualizer()
    
    # Create a sample linked list: 1 -> 3 -> 5 -> 7
    head = Node(1)
    head.next = Node(3)
    head.next.next = Node(5)
    head.next.next.next = Node(7)
    
    # Initial state
    visualizer.draw_structure(head, hold_time=2)
    
    # Insert 4 at position 2
    head = visualizer.animate_operation("insert", head, 4, 2, hold_time=2)
    
    # Delete node at position 1
    head = visualizer.animate_operation("delete", head, 1, hold_time=2)
    
    # Create video - each frame will show for the correct duration
    visualizer.video_writer.create_video(fps=30)
    visualizer.cleanup()