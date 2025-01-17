from typing import List, Any, Optional, Tuple
from abc import ABC
from base_visualizer import Cell, ElementStyle, ConnectorStyle, Renderer

class Node:
    def __init__(self, value: int):
        self.value = value
        self.next: Optional['Node'] = None

class LinkedListOperation(ABC):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, *args, hold_time: float = 2.0, **kwargs) -> Node:
        pass

class InsertOperation(LinkedListOperation):
    """Inserts a new node at the specified position.
    Usage: {"action": "insert", "target": "list[1]", "properties": {"value": 42}}
    """
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, value: int, position: int, hold_time: float = 2.0, draw_callback = None) -> Node:
        new_node = Node(value)
        
        if position == 0:
            new_node.next = head
            head = new_node
            visualizer.renderer.clear_screen()
            visualizer.draw_structure(head, highlighted_elements=[value])
            if draw_callback:
                draw_callback()
            for _ in range(int(hold_time * 30)):
                visualizer.renderer.video_writer.save_frame(visualizer.renderer.screen)
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
        
        visualizer.renderer.clear_screen()
        visualizer.draw_structure(head, highlighted_elements=[value])
        if draw_callback:
            draw_callback()
        for _ in range(int(hold_time * 30)):
            visualizer.renderer.video_writer.save_frame(visualizer.renderer.screen)
        return head

class DeleteOperation(LinkedListOperation):
    """Deletes a node at the specified position.
    Usage: {"action": "delete", "target": "list[1]"}
    """
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, position: int, hold_time: float = 2.0, draw_callback = None) -> Node:
        if not head:
            return None
        
        if position == 0:
            head = head.next
            visualizer.renderer.clear_screen()
            visualizer.draw_structure(head)
            if draw_callback:
                draw_callback()
            for _ in range(int(hold_time * 30)):
                visualizer.renderer.video_writer.save_frame(visualizer.renderer.screen)
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
        visualizer.renderer.clear_screen()
        visualizer.draw_structure(head)
        if draw_callback:
            draw_callback()
        for _ in range(int(hold_time * 30)):
            visualizer.renderer.video_writer.save_frame(visualizer.renderer.screen)
        return head

class LinkedListVisualizer:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.element_style = ElementStyle()
        self.connector_style = ConnectorStyle()
        self.cells: List[Cell] = []
        self.operations = {
            "insert": InsertOperation(),
            "delete": DeleteOperation()
        }
        self.position: Optional[Tuple[int, int]] = None

    def create_cells(self, head: Node, position: Optional[Tuple[int, int]] = None) -> List[Cell]:
        cells = []
        current = head
        
        node_count = 0
        temp = head
        while temp:
            node_count += 1
            temp = temp.next
        
        self.element_style.adjust_for_count(
            node_count,
            self.renderer.config.width * 0.9
        )
        
        total_width = node_count * (self.element_style.width + self.element_style.spacing) - self.element_style.spacing
        
        if position:
            start_x, y = position
        else:
            start_x = (self.renderer.config.width - total_width) // 2
            y = self.renderer.config.default_y
        
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
    
    def animate_operation(self, operation_name: str, *args, hold_time: float = 2.0, **kwargs) -> Node:
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")
        return self.operations[operation_name].animate(self, *args, hold_time=hold_time, **kwargs)

    def draw_structure(self, data_structure: Node, highlighted_elements: Optional[List[Any]] = None) -> None:
        self.cells = self.create_cells(data_structure, self.position)
        
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