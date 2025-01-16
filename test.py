from linked_list_visualizer import LinkedListVisualizer, Node
from array_visualizer import ArrayVisualizer
from base_visualizer import BaseVisualizerConfig, Renderer, VideoWriter
from command_processor import CommandProcessor
import os
import glob
import pygame
import json

if __name__ == "__main__":
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    
    for f in glob.glob("frames/*.png"):
        os.remove(f)
    
    config = BaseVisualizerConfig(width=800, height=600)
    video_writer = VideoWriter()
    renderer = Renderer(config, video_writer)
    
    command_processor = CommandProcessor(renderer)
    
    array1 = [2, 4, 6, 8]
    array2 = [1, 3, 5, 7]
    
    command_processor.add_data_structure("array1", array1, "array", (100, 150))
    command_processor.add_data_structure("array2", array2, "array", (100, 350))
    
    commands = [
        {
            "action": "highlight",
            "target": "array1[0]",
            "properties": {"color": "red", "duration": "1s"},
            "step": 1,
            "text": {"content": "Looking at first array", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "We start with the first array", "duration": "2s"}
        },
        {
            "action": "highlight",
            "target": "array2[0]",
            "properties": {"color": "red", "duration": "1s"},
            "step": 2,
            "text": {"content": "Now looking at second array", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "Then we look at the second array", "duration": "2s"}
        },
        {
            "action": "compare",
            "target": "array1[0],array1[3]",
            "properties": {"duration": "2s"},
            "step": 3,
            "text": {"content": "Compare elements in first array", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "Comparing elements in the first array", "duration": "2s"}
        },
        {
            "action": "compare",
            "target": "array2[0],array2[3]",
            "properties": {"duration": "2s"},
            "step": 4,
            "text": {"content": "Compare elements in second array", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "Comparing elements in the second array", "duration": "2s"}
        }
    ]
    
    renderer.clear_screen()
    for command in commands:
        command_processor.process_command(json.dumps(command))
    
    list1 = Node(1)
    list1.next = Node(3)
    list1.next.next = Node(5)
    
    list2 = Node(2)
    list2.next = Node(4)
    list2.next.next = Node(6)
    
    command_processor.add_data_structure("list1", list1, "linked_list", (100, 450))
    command_processor.add_data_structure("list2", list2, "linked_list", (100, 550))
    
    list_commands = [
        {
            "action": "highlight",
            "target": "list1[1]",
            "properties": {"duration": "1s"},
            "step": 5,
            "text": {"content": "Highlight node in first list", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "Looking at the second node in the first list", "duration": "2s"}
        },
        {
            "action": "highlight",
            "target": "list2[1]",
            "properties": {"duration": "1s"},
            "step": 6,
            "text": {"content": "Highlight node in second list", "pre_duration": "0.5s", "post_duration": "1s"},
            "transcript": {"content": "Looking at the second node in the second list", "duration": "2s"}
        }
    ]
    
    for command in list_commands:
        command_processor.process_command(json.dumps(command))
    
    video_writer.create_video("animation.mp4", fps=30)
    pygame.quit()