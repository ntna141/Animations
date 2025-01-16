from typing import List, Any, Optional, Tuple
from base_visualizer import Cell, ElementStyle, ConnectorStyle, Renderer, DataStructureState

class ArrayVisualizer:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.element_style = ElementStyle()
        self.connector_style = ConnectorStyle()
        self.cells: List[Cell] = []
        self.position: Optional[Tuple[int, int]] = None
        self.current_state = DataStructureState()
    
    def create_state_from_array(self, array: List[int], highlighted: Optional[List[int]] = None, 
                              arrows: Optional[List[Tuple[int, int]]] = None) -> DataStructureState:
        state = DataStructureState()
        state.elements = array.copy()
        
        if self.position:
            center_x, y = self.position
        else:
            center_x = self.renderer.config.width // 2
            y = self.renderer.config.default_y
            
        center_idx = (len(array) - 1) // 2
        cell_spacing = self.element_style.width + self.element_style.spacing
        
        for i in range(len(array)):
            offset_from_center = i - center_idx
            x = center_x + (offset_from_center * cell_spacing)
            state.positions[i] = (x, y)
        
        if highlighted:
            state.highlighted = highlighted
            
        if arrows:
            state.arrows = arrows.copy()
            
        return state
    
    def draw_state(self, state: DataStructureState) -> None:
        self.cells = []
        
        for i, value in enumerate(state.elements):
            if i in state.positions:
                x, y = state.positions[i]
                cell = Cell(value, 
                          x - self.element_style.width // 2,
                          y,
                          self.element_style.width,
                          self.element_style.height)
                cell.highlighted = i in state.highlighted
                self.cells.append(cell)
                self.renderer.draw_cell(cell, self.element_style)
        
        for from_idx, to_idx in state.arrows:
            if from_idx < len(self.cells) and to_idx < len(self.cells):
                self.renderer.draw_connection(
                    self.cells[from_idx],
                    self.cells[to_idx],
                    self.connector_style,
                    curved=True,
                    double_ended=True
                )
    
    def animate_to_state(self, target_state: DataStructureState, duration: float = 1.0) -> None:
        fps = 30
        total_frames = int(duration * fps)
        
        for frame in range(total_frames + 1):
            progress = frame / total_frames if total_frames > 0 else 1.0
            
            intermediate_state = self.current_state.interpolate(target_state, progress)
            
            self.renderer.clear_screen()
            self.draw_state(intermediate_state)
            self.renderer.video_writer.save_frame(self.renderer.screen)
        
        self.current_state = target_state
    
    def _animate_swap(self, array: List[int], idx1: int, idx2: int, hold_time: float = 2.0, draw_callback = None) -> List[int]:
        initial_state = self.create_state_from_array(array, highlighted=[idx1, idx2])
        
        swapped_array = array.copy()
        swapped_array[idx1], swapped_array[idx2] = swapped_array[idx2], swapped_array[idx1]
        target_state = self.create_state_from_array(swapped_array, highlighted=[idx1, idx2])
        
        pos1 = target_state.positions[idx1]
        pos2 = target_state.positions[idx2]
        target_state.positions[idx1] = pos2
        target_state.positions[idx2] = pos1
        
        self.animate_to_state(target_state, duration=hold_time)
        
        if draw_callback:
            draw_callback()
        
        return swapped_array
    
    def animate_operation(self, operation_name: str, *args, hold_time: float = 2.0, draw_callback = None, **kwargs) -> List[int]:
        if operation_name == "swap":
            return self._animate_swap(*args, hold_time=hold_time, draw_callback=draw_callback, **kwargs)
        return args[0]
    
    def draw_structure(self, array: List[int], highlighted_elements: Optional[List[Any]] = None) -> None:
        state = self.create_state_from_array(array, highlighted=[i for i, x in enumerate(array) if x in (highlighted_elements or [])])
        self.current_state = state
        self.draw_state(state)