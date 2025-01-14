from typing import List, Any, Optional
from base_visualizer import DataStructureVisualizer, Cell

class ArrayVisualizer(DataStructureVisualizer[List[int]]):
    def create_cells(self, array: List[int]) -> List[Cell]:
        total_width = len(array) * (self.element_style.width + self.element_style.spacing) - self.element_style.spacing
        start_x = (self.config.width - total_width) // 2
        y = self.config.height // 2 - self.element_style.height // 2
        
        return [
            Cell(value, 
                 start_x + i * (self.element_style.width + self.element_style.spacing),
                 y,
                 self.element_style.width,
                 self.element_style.height)
            for i, value in enumerate(array)
        ]
    
    def _animate_swap(self, array: List[int], idx1: int, idx2: int, hold_time: float = 2.0) -> List[int]:
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        self._hold_frame(hold_time)
        
        cell1 = self.cells[idx1]
        cell2 = self.cells[idx2]
        self.renderer.draw_connection(cell1, cell2, self.connector_style, curved=True, double_ended=True)
        
        self.renderer.update_display()
        self.video_writer.save_frame(self.renderer.screen)
        self._hold_frame(hold_time)
        
        array[idx1], array[idx2] = array[idx2], array[idx1]
        
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        self._hold_frame(hold_time)
        
        return array
    
    def animate_operation(self, operation_name: str, *args, hold_time: float = 2.0, **kwargs) -> None:
        if operation_name == "swap":
            self._animate_swap(*args, hold_time=hold_time, **kwargs)
    
    def draw_structure(self, array: List[int], highlighted_elements: Optional[List[Any]] = None, hold_time: float = 2) -> None:
        self.renderer.clear_screen()
        
        self.cells = self.create_cells(array)
        
        if highlighted_elements:
            for cell in self.cells:
                cell.highlighted = cell.value in highlighted_elements
        
        for cell in self.cells:
            self.renderer.draw_cell(cell, self.element_style)
        
        self.renderer.update_display()
        self.video_writer.save_frame(self.renderer.screen)
        
        if hold_time > 0:
            frames = int(hold_time * 30)
            for _ in range(frames):
                self.video_writer.save_frame(self.renderer.screen)