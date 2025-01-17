from typing import List, Dict, Any, Optional
import json
from command_processor import CommandProcessor
from base_visualizer import BaseVisualizerConfig, Renderer, VideoWriter, DataStructureVisualizer
from linked_list_visualizer import Node
import os
import glob
import pygame
import inspect
from array_visualizer import ArrayVisualizer
from linked_list_visualizer import LinkedListVisualizer, InsertOperation, DeleteOperation

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

def get_available_commands(data_structure_type: str) -> Dict[str, Any]:
    """Get available commands and their documentation for a given data structure type.
    
    Common capabilities across all visualizations:
    - Text display: Upper text, middle text, and transcript text can be shown
    - Code highlighting: Any line of code can be highlighted with optional comments
    - Duration control: All animations can specify duration in seconds (e.g. "2s")
    - Multiple diagrams: Can create and switch between multiple visualizations
    """
    
    base_properties = {
        "duration": "Duration in seconds (e.g., '2s')",
        "diagram_name": "Name of diagram to create/switch to",
        "initial_data": "Initial data for new diagram",
        "position": "Position for new diagram (x,y)",
        "text": {
            "content": "Text explanation to display",
            "pre_duration": "Time to show text before animation (default '1s')",
            "post_duration": "Time to show text after animation (default '2s')"
        },
        "transcript": {
            "content": "Detailed explanation for transcript area",
            "duration": "How long to display the transcript"
        },
        "code_lines": {
            "line": "Line number to highlight in code",
            "comment": "Optional comment to show next to highlighted line"
        }
    }
    
    base_actions = [
        "new_diagram", 
        "switch_diagram" 
    ]
    
    visualizer_map = {
        "array": ArrayVisualizer,
        "linked_list": LinkedListVisualizer
    }
    
    if data_structure_type not in visualizer_map:
        return {}
    
    visualizer_class = visualizer_map[data_structure_type]
    commands = {
        "actions": base_actions.copy(),
        "properties": base_properties.copy(),
    }
    
    
    if data_structure_type == "array":
        commands["actions"].extend(["highlight", "swap", "compare"])
        commands["target_format"] = "array[index] or array[index1],array[index2]"
        commands["properties"]["color"] = "Color for highlighting (e.g., 'red')"
        
        commands["operations"] = {
            "swap": """Swaps two elements in the array with animation.
                    Usage: {"action": "swap", "target": "array[0],array[1]"}
                    Features:
                    - Animates elements smoothly moving to their new positions
                    - Highlights swapped elements
                    - Can specify custom duration""",
            
            "highlight": """Highlights specified elements in the array.
                        Usage: {"action": "highlight", "target": "array[0]"} or {"action": "highlight", "target": "array[0],array[1]"}
                        Features:
                        - Can highlight single or multiple elements
                        - Customizable highlight color
                        - Can add labels or pointers above elements
                        - Can specify custom duration""",
            
            "compare": """Shows comparison between two elements with a curved arrow.
                      Usage: {"action": "compare", "target": "array[0],array[1]"}
                      Features:
                      - Draws curved double-ended arrow between elements
                      - Highlights compared elements
                      - Can customize arrow style and color
                      - Can specify custom duration"""
        }
        
    elif data_structure_type == "linked_list":
        commands["actions"].extend(["highlight", "insert", "delete"])
        commands["target_format"] = "list[position]"
        commands["properties"]["value"] = "Value to insert (only for insert)"
        
        commands["operations"] = {
            "insert": """Inserts a new node at the specified position.
                     Usage: {"action": "insert", "target": "list[1]", "properties": {"value": 42}}
                     Features:
                     - Animates node insertion
                     - Updates connections smoothly
                     - Highlights new node
                     - Can insert at any valid position
                     - Can specify custom duration""",
            
            "delete": """Deletes a node at the specified position.
                     Usage: {"action": "delete", "target": "list[1]"}
                     Features:
                     - Animates node removal
                     - Updates connections smoothly
                     - Can delete from any valid position
                     - Can specify custom duration""",
            
            "highlight": """Highlights specified node in the linked list.
                       Usage: {"action": "highlight", "target": "list[1]"}
                       Features:
                       - Can highlight any node by position
                       - Can add labels or pointers above nodes
                       - Customizable highlight color
                       - Can specify custom duration"""
        }
    
    return commands

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
    
    array_solution = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
    """
    
    
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