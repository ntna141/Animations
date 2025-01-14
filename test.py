from linked_list_visualizer import LinkedListVisualizer, Node
from array_visualizer import ArrayVisualizer
from base_visualizer import BaseVisualizerConfig, Renderer, VideoWriter
import os
import glob
import pygame

if __name__ == "__main__":
    # Initialize pygame once at the start
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    
    # Clean up any existing frames
    for f in glob.glob("frames/*.png"):
        os.remove(f)
    
    # Create shared config, video writer, and renderer
    config = BaseVisualizerConfig(width=800, height=600)
    video_writer = VideoWriter()
    renderer = Renderer(config, video_writer)
    
    # Create visualizers that share the same renderer
    list_visualizer = LinkedListVisualizer(renderer)
    array_visualizer = ArrayVisualizer(renderer)
    
    # Create initial data structures
    head = Node(1)
    head.next = Node(3)
    head.next.next = Node(5)
    head.next.next.next = Node(7)
    
    array = [2, 4, 6, 8]
    
    def draw_both():
        renderer.clear_screen()
        list_visualizer.draw_structure(head)
        array_visualizer.draw_structure(array)
        video_writer.save_frame(renderer.screen)
    
    # Show initial state of both structures
    draw_both()
    
    # Hold initial state
    for _ in range(int(2 * 30)):  # 2 seconds at 30fps
        video_writer.save_frame(renderer.screen)
    
    # Interleave operations:
    # 1. Array swap first and last
    array = array_visualizer.animate_operation("swap", array, 0, 3, hold_time=2, draw_callback=lambda: list_visualizer.draw_structure(head))
    
    # 2. List insert 4 at position 2
    head = list_visualizer.animate_operation("insert", head, 4, 2, hold_time=2, draw_callback=lambda: array_visualizer.draw_structure(array))
    
    # 3. Array swap middle elements
    array = array_visualizer.animate_operation("swap", array, 1, 2, hold_time=2, draw_callback=lambda: list_visualizer.draw_structure(head))
    
    # 4. List delete at position 1
    head = list_visualizer.animate_operation("delete", head, 1, hold_time=2, draw_callback=lambda: array_visualizer.draw_structure(array))
    
    # Create video
    video_writer.create_video("animation.mp4", fps=30)
    
    # Cleanup pygame at the very end
    pygame.quit()