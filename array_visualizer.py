from typing import List, Any, Optional
from base_visualizer import Cell, ElementStyle, ConnectorStyle, Renderer

class ArrayVisualizer:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.element_style = ElementStyle()
        self.connector_style = ConnectorStyle()
        self.cells: List[Cell] = []
    
    def create_cells(self, array: List[int]) -> List[Cell]:
        total_width = len(array) * (self.element_style.width + self.element_style.spacing) - self.element_style.spacing
        start_x = (self.renderer.config.width - total_width) // 2
        y = (self.renderer.config.height * 3) // 4 - self.element_style.height // 2
        
        return [
            Cell(value, 
                 start_x + i * (self.element_style.width + self.element_style.spacing),
                 y,
                 self.element_style.width,
                 self.element_style.height)
            for i, value in enumerate(array)
        ]
    
    def _animate_swap(self, array: List[int], idx1: int, idx2: int, hold_time: float = 2.0, draw_callback = None) -> List[int]:
        # Clear and redraw both structures
        self.renderer.clear_screen()
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        if draw_callback:
            draw_callback()
        
        cell1 = self.cells[idx1]
        cell2 = self.cells[idx2]
        self.renderer.draw_connection(cell1, cell2, self.connector_style, curved=True, double_ended=True)
        
        # Hold the frame
        for _ in range(int(hold_time * 30)):
            self.renderer.video_writer.save_frame(self.renderer.screen)
        
        array[idx1], array[idx2] = array[idx2], array[idx1]
        
        # Clear and redraw final state
        self.renderer.clear_screen()
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        if draw_callback:
            draw_callback()
        
        # Hold the frame
        for _ in range(int(hold_time * 30)):
            self.renderer.video_writer.save_frame(self.renderer.screen)
        
        return array
    
    def animate_operation(self, operation_name: str, *args, hold_time: float = 2.0, draw_callback = None, **kwargs) -> List[int]:
        if operation_name == "swap":
            return self._animate_swap(*args, hold_time=hold_time, draw_callback=draw_callback, **kwargs)
        return args[0]  # Return the array unchanged if operation not recognized
    
    def draw_structure(self, array: List[int], highlighted_elements: Optional[List[Any]] = None) -> None:
        self.cells = self.create_cells(array)
        
        if highlighted_elements:
            for cell in self.cells:
                cell.highlighted = cell.value in highlighted_elements
        
        for cell in self.cells:
            self.renderer.draw_cell(cell, self.element_style)