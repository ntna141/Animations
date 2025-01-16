from typing import List, Dict, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass
import json
import re
from base_visualizer import Renderer, ElementStyle, ConnectorStyle, DataStructureState
from array_visualizer import ArrayVisualizer
from linked_list_visualizer import LinkedListVisualizer, Node

@dataclass
class VisualizationCommand:
    step: int
    target: str
    state: Dict[str, Any]
    duration: Optional[str] = "2s"
    line: Optional[int] = None
    text: Optional[str] = None
    action: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    code_lines: Optional[Dict[str, Any]] = None
    transcript: Optional[Dict[str, Any]] = None

class CommandProcessor:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.video_writer = renderer.video_writer
        self.current_step = 0
        self.visualizers: Dict[str, Union[ArrayVisualizer, LinkedListVisualizer]] = {}
        self.data_structures: Dict[str, Dict[str, Any]] = {}
        self.current_screen = "main"
        self.screens: Dict[str, Set[str]] = {"main": set()}
        
        screen_top = self.renderer.config.height // 4
        self.default_positions = {
            1: [(self.renderer.config.width // 2, screen_top)],
            2: [
                (self.renderer.config.width // 2, screen_top - 100),
                (self.renderer.config.width // 2, screen_top + 100)
            ]
        }
    
    def get_default_position(self, screen: str) -> Tuple[int, int]:
        structures_in_screen = len(self.screens.get(screen, set()))
        screen_top = self.renderer.config.height // 4
        
        if structures_in_screen < len(self.default_positions[1]):
            return self.default_positions[1][structures_in_screen]
        elif structures_in_screen < len(self.default_positions[2]):
            return self.default_positions[2][structures_in_screen]
        
        row = (structures_in_screen - 2) // 2
        col = (structures_in_screen - 2) % 2
        x = self.renderer.config.width // 2 + (col * 300 - 150)
        y = screen_top + (row * 150)
        return (x, y)

    def add_data_structure(self, name: str, data: Union[List[int], Node], structure_type: str, screen: str = "main", position: Optional[Tuple[int, int]] = None) -> None:
        if screen not in self.screens:
            self.screens[screen] = set()
        
        self.screens[screen].add(name)
        
        if position is None:
            position = self.get_default_position(screen)
            
        is_single_structure = len(self.screens[screen]) == 1
        element_style = ElementStyle()
        
        if not is_single_structure:
            element_style.width = element_style.base_size // 2
            element_style.height = element_style.base_size // 2
            element_style.spacing = element_style.base_size // 6
        
        if name != "main":
            element_style.color = (150, 200, 150)
            
        if isinstance(data, list):
            data_copy = data.copy()
            visualizer = ArrayVisualizer(self.renderer)
            visualizer.element_style = element_style
            self.visualizers[name] = visualizer
        else:
            curr = data
            if curr:
                head = Node(curr.value)
                new_curr = head
                curr = curr.next
                while curr:
                    new_curr.next = Node(curr.value)
                    new_curr = new_curr.next
                    curr = curr.next
                data_copy = head
            else:
                data_copy = None
            visualizer = LinkedListVisualizer(self.renderer)
            visualizer.element_style = element_style
            self.visualizers[name] = visualizer

        self.data_structures[name] = {
            "type": structure_type,
            "data": data_copy,
            "position": position,
            "screen": screen
        }
        
        visualizer = self.visualizers[name]
        visualizer.position = position
        
        if isinstance(data, list):
            initial_state = visualizer.create_state_from_array(data_copy)
            visualizer.current_state = initial_state
            visualizer.draw_state(initial_state)

    def process_command(self, command_json: str) -> None:
        command_dict = json.loads(command_json)
        command = VisualizationCommand(**command_dict)
        
        structure_name = command.target
        if structure_name not in self.data_structures:
            print(f"Unknown structure: {structure_name}")
            return
            
        structure_info = self.data_structures[structure_name]
        visualizer = self.visualizers[structure_name]
        
        if structure_info["type"] == "array":
            target_state = visualizer.create_state_from_array(
                command.state["elements"],
                highlighted=command.state.get("highlighted", []),
                arrows=command.state.get("arrows", [])
            )
            
            duration = float(command.duration.rstrip("s"))
            
            if command.text:
                self.renderer.set_transcript(command.text)
            
            if command.line:
                self.renderer.highlight_code_line(command.line)
            
            visualizer.animate_to_state(target_state, duration=duration)
            
            structure_info["data"] = command.state["elements"]
            self.data_structures[structure_name] = structure_info
        
        self.current_step = command.step
    
    def _extract_indices(self, target: str) -> List[int]:
        indices = []
        for match in re.finditer(r"\[(\d+)\]", target):
            indices.append(int(match.group(1)))
        return indices
    
    def _extract_list_position(self, target: str) -> Optional[int]:
        match = re.search(r"\[(\d+)\]", target)
        return int(match.group(1)) if match else None
    
    def _process_array_command(self, action: str, target: str, properties: Dict[str, Any], structure_info: Dict[str, Any]) -> None:
        array_data = structure_info["data"]
        if not isinstance(array_data, list):
            return
            
        self.array_visualizer.position = structure_info["position"]
            
        if action == "highlight":
            indices = self._extract_indices(target)
            if indices:
                highlighted = [array_data[i] for i in indices]
                self.array_visualizer.draw_structure(array_data, highlighted_elements=highlighted)
        elif action == "swap":
            indices = self._extract_indices(target)
            if len(indices) == 2:
                array_data[indices[0]], array_data[indices[1]] = array_data[indices[1]], array_data[indices[0]]
                self.array_visualizer.draw_structure(array_data, highlighted_elements=[array_data[indices[0]], array_data[indices[1]]])
        elif action == "compare":
            indices = self._extract_indices(target)
            if len(indices) == 2:
                highlighted = [array_data[i] for i in indices]
                self.array_visualizer.draw_structure(array_data, highlighted_elements=highlighted)
                cell1 = self.array_visualizer.cells[indices[0]]
                cell2 = self.array_visualizer.cells[indices[1]]
                self.renderer.draw_connection(cell1, cell2, self.array_visualizer.connector_style, 
                                           curved=True, double_ended=True)
    
    def _process_list_command(self, action: str, target: str, properties: Dict[str, Any], structure_info: Dict[str, Any]) -> None:
        list_data = structure_info["data"]
        if not isinstance(list_data, Node):
            return
            
        self.list_visualizer.position = structure_info["position"]
            
        if action == "highlight":
            pos = self._extract_list_position(target)
            if pos is not None:
                current = list_data
                for _ in range(pos):
                    if not current:
                        return
                    current = current.next
                if current:
                    self.list_visualizer.draw_structure(list_data, highlighted_elements=[current.value])
        elif action == "insert":
            pos = self._extract_list_position(target)
            value = properties.get("value")
            if pos is not None and value is not None:
                structure_info["data"] = self.list_visualizer.animate_operation(
                    "insert", list_data, value, pos,
                    hold_time=float(properties.get("duration", "1").rstrip("s"))
                )
        elif action == "delete":
            pos = self._extract_list_position(target)
            if pos is not None:
                structure_info["data"] = self.list_visualizer.animate_operation(
                    "delete", list_data, pos,
                    hold_time=float(properties.get("duration", "1").rstrip("s"))
                ) 