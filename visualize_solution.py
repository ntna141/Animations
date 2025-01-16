from typing import List, Dict, Any, Optional
import json
from command_processor import CommandProcessor
from base_visualizer import BaseVisualizerConfig, Renderer, VideoWriter, DataStructureVisualizer
from linked_list_visualizer import Node
import os
import glob
import pygame

class SolutionVisualizer(DataStructureVisualizer):
    def __init__(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        for f in glob.glob("frames/*.png"):
            os.remove(f)
        
        super().__init__(BaseVisualizerConfig(width=1080, height=1920))
        
        self.command_processor = CommandProcessor(self.renderer)
    
    def create_cells(self, data_structure: Any) -> List[Any]:
        return []
    
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        pass
    
    def create_visualization(self, 
                           initial_data: Any,
                           data_structure_type: str,
                           commands: List[Dict[str, Any]],
                           output_file: str = "animation.mp4") -> None:
        self.command_processor.add_data_structure("main_array", initial_data, data_structure_type, "main")
        
        self.renderer.clear_screen()
        structure_info = self.command_processor.data_structures["main_array"]
        visualizer = self.command_processor.visualizers["main_array"]
        visualizer.draw_structure(structure_info["data"])
        self.video_writer.save_frame(self.renderer.screen)
        
        for _ in range(int(1 * 30)):
            self.video_writer.save_frame(self.renderer.screen)
        
        for command in commands:
            if isinstance(command, dict):
                target = command.get("target", "")
                if target.startswith("array[") or target.startswith("list["):
                    current_screen = self.command_processor.current_screen
                    screen_structures = self.command_processor.screens[current_screen]
                    
                    if len(screen_structures) == 1:
                        structure_name = next(iter(screen_structures))
                        command["target"] = f"{structure_name}{target[target.find('['):]}"
                    elif target.startswith("array["):
                        command["target"] = f"main_array{target[target.find('['):]}"
                    
            self.command_processor.process_command(json.dumps(command))
        
        self.video_writer.create_video(output_file, fps=30)

def get_available_commands(data_structure_type: str) -> Dict[str, List[str]]:
    commands = {
        "array": {
            "actions": ["highlight", "swap", "compare", "new_diagram", "switch_diagram"],
            "target_format": "array[index] or array[index1],array[index2]",
            "properties": {
                "color": "Color for highlighting (e.g., 'red')",
                "duration": "Duration in seconds (e.g., '2s')",
                "diagram_name": "Name of diagram to create/switch to",
                "initial_data": "Initial data for new diagram",
                "position": "Position for new diagram (x,y)"
            }
        },
        "linked_list": {
            "actions": ["highlight", "insert", "delete", "new_diagram", "switch_diagram"],
            "target_format": "list[position]",
            "properties": {
                "value": "Value to insert (only for insert)",
                "duration": "Duration in seconds (e.g., '2s')",
                "diagram_name": "Name of diagram to create/switch to",
                "initial_data": "Initial data for new diagram",
                "position": "Position for new diagram (x,y)"
            }
        }
    }
    return commands.get(data_structure_type, {})

def format_command_template(data_structure_type: str) -> str:
    base_template = {
        "action": "<action>",
        "target": f"{data_structure_type}[i]",
        "properties": {
            "duration": "2s",
            "diagram_name": "optional - name of diagram",
            "initial_data": "optional - data for new diagram",
            "position": "optional - [x, y] position",
            "style": {
                "color": [100, 100, 100],
                "size": 60
            }
        },
        "step": 1,
        "transcript": {
            "content": "Code explanation",
            "duration": "3s"
        },
        "code_lines": {
            "3": "Check if current element needs to be swapped"
        }
    }
    return json.dumps(base_template, indent=4)

if __name__ == "__main__":
    # Example array-based solution
    array_solution = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """
    
    # Example commands for bubble sort visualization
    initial_array = [64, 34, 25, 12]
    commands = [
        {
            "action": "highlight",
            "target": "array[0],array[1]",
            "properties": {"color": "red", "duration": "1s"},
            "step": 1,
            "text": "Compare first two elements",
            "transcript": "Looking at elements 64 and 34"
        },
        {
            "action": "compare",
            "target": "array[0],array[1]",
            "properties": {"duration": "1s"},
            "step": 2,
            "text": "64 > 34, need to swap",
            "transcript": "Since 64 is greater than 34, we'll swap them"
        },
        {
            "action": "swap",
            "target": "array[0],array[1]",
            "properties": {"duration": "1.5s"},
            "step": 3,
            "text": "Swap elements",
            "transcript": "Swapping 64 and 34"
        }
    ]
    
    visualizer = SolutionVisualizer()
    visualizer.create_visualization(initial_array, "array", commands)
    visualizer.cleanup()
    
    print("\nAvailable commands for arrays:")
    print(format_command_template("array"))
    
    print("\nAvailable commands for linked lists:")
    print(format_command_template("linked_list")) 