from typing import List, Any, Optional
from abc import ABC
from base_visualizer import DataStructureVisualizer, Cell, BaseVisualizerConfig
import pygame

class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: Optional['Node'] = None

class LinkedListOperation(ABC):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, *args, hold_time: float = 2.0, **kwargs) -> Node:
        pass

class InsertOperation(LinkedListOperation):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, value: int, position: int, hold_time: float = 2.0) -> Node:
        new_node = Node(value)
        
        if position == 0:
            new_node.next = head
            head = new_node
            visualizer.draw_structure(head, highlighted_elements=[value], hold_time=hold_time)
            return head
        
        current = head
        for i in range(position - 1):
            if current is None:
                return head
            current = current.next
        
        if current is None:
            return head
        
        new_node.next = current.next
        current.next = new_node
        
        visualizer.draw_structure(head, highlighted_elements=[value], hold_time=hold_time)
        return head

class DeleteOperation(LinkedListOperation):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, position: int, hold_time: float = 2.0) -> Node:
        if not head:
            return None
        
        if position == 0:
            value_to_delete = head.value
            head = head.next
            visualizer.draw_structure(head, hold_time=hold_time)
            return head
        
        current = head
        prev = None
        for i in range(position):
            if current is None:
                return head
            prev = current
            current = current.next
        
        if current is None:
            return head
        
        prev.next = current.next
        visualizer.draw_structure(head, hold_time=hold_time)
        return head

class LinkedListVisualizer(DataStructureVisualizer[Node]):
    def __init__(self, config: Optional[BaseVisualizerConfig] = None):
        super().__init__(config)
        self.operations = {
            "insert": InsertOperation(),
            "delete": DeleteOperation()
        }

    def cleanup(self):
        pygame.quit()

    def create_cells(self, head: Node) -> List[Cell]:
        cells = []
        current = head
        
        node_count = 0
        temp = head
        while temp:
            node_count += 1
            temp = temp.next
        
        total_width = node_count * (self.element_style.width + self.element_style.spacing) - self.element_style.spacing
        start_x = (self.config.width - total_width) // 2
        y = self.config.height // 2 - self.element_style.height // 2
        
        prev_cell = None
        i = 0
        while current:
            cell = Cell(
                current.value,
                start_x + i * (self.element_style.width + self.element_style.spacing),
                y,
                self.element_style.width,
                self.element_style.height
            )
            
            if prev_cell:
                prev_cell.connect_to(cell)
            
            cells.append(cell)
            prev_cell = cell
            current = current.next
            i += 1
            
        return cells
    
    def animate_operation(self, operation_name: str, *args, hold_time: float = 2.0, **kwargs) -> None:
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")
        return self.operations[operation_name].animate(self, *args, hold_time=hold_time, **kwargs)

    def draw_structure(self, data_structure: Node, highlighted_elements: Optional[List[Any]] = None, hold_time: float = 0) -> None:
        self.renderer.clear_screen()
        
        self.cells = self.create_cells(data_structure)
        
        if highlighted_elements:
            for cell in self.cells:
                cell.highlighted = cell.value in highlighted_elements
        
        for i in range(len(self.cells) - 1):
            cell = self.cells[i]
            next_cell = self.cells[i + 1]
            self.renderer.draw_cell(cell, self.element_style)
            self.renderer.draw_connection(cell, next_cell, self.connector_style, curved=False)
            
        if self.cells:
            self.renderer.draw_cell(self.cells[-1], self.element_style)
        
        self.renderer.update_display()
        self.save_frame(hold_time)