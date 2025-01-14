from abc import ABC, abstractmethod
from dataclasses import dataclass
import pygame
import cv2
import os
import glob
import math
from typing import List, Dict, Optional, Tuple, Any, Generic, TypeVar, Set

T = TypeVar('T')  # Generic type for different data structures

@dataclass
class BaseVisualizerConfig:
    """Base configuration that all visualizers will inherit from"""
    width: int = 800
    height: int = 400
    background_color: Tuple[int, int, int] = (255, 255, 255)  # White
    text_color: Tuple[int, int, int] = (0, 0, 0)            # Black
    font_size: int = 36
    animation_frames: int = 30

@dataclass
class ElementStyle:
    """Style configuration for individual elements"""
    width: int = 60
    height: int = 60
    spacing: int = 20
    color: Tuple[int, int, int] = (100, 100, 100)      # Gray
    highlight_color: Tuple[int, int, int] = (255, 200, 200)  # Light red

@dataclass
class ConnectorStyle:
    """Style configuration for connectors (arrows, lines, etc.)"""
    color: Tuple[int, int, int] = (0, 100, 200)    # Blue
    thickness: int = 3
    head_size: int = 15

class Cell:
    """Represents a single cell in any data structure"""
    def __init__(self, value: Any, x: int, y: int, width: int, height: int):
        self.value = value
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connections: Set['Cell'] = set()
        self.highlighted = False
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def connect_to(self, other: 'Cell') -> None:
        """Create a bidirectional connection between cells"""
        self.connections.add(other)
        other.connections.add(self)
    
    def disconnect_from(self, other: 'Cell') -> None:
        """Remove bidirectional connection between cells"""
        self.connections.discard(other)
        other.connections.discard(self)

class Renderer:
    """Base rendering class that handles pygame initialization and basic drawing"""
    def __init__(self, config: BaseVisualizerConfig):
        pygame.init()
        self.config = config
        self.screen = pygame.display.set_mode((config.width, config.height))
        self.font = pygame.font.Font(None, config.font_size)
    
    def clear_screen(self):
        self.screen.fill(self.config.background_color)
    
    def draw_text(self, text: str, position: Tuple[int, int], center: bool = True) -> pygame.Rect:
        text_surface = self.font.render(str(text), True, self.config.text_color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_cell(self, cell: Cell, style: ElementStyle) -> None:
        """Draw a single cell with its value"""
        if cell.highlighted:
            self.draw_rect(cell.rect, style.highlight_color)
        self.draw_rect(cell.rect, style.color, 2)
        self.draw_text(str(cell.value), cell.center)
    
    def draw_connection(self, start_cell: Cell, end_cell: Cell, 
                       style: ConnectorStyle, curved: bool = True,
                       double_ended: bool = False) -> None:
        """Draw a connection (arrow) between two cells"""
        if curved:
            self.draw_curved_arrow(start_cell.center, end_cell.center, 
                                 style, double_ended=double_ended)
        else:
            self.draw_straight_arrow(start_cell.center, end_cell.center, 
                                   style, double_ended=double_ended)
    
    def draw_rect(self, rect: pygame.Rect, color: Tuple[int, int, int], 
                 border_width: int = 0) -> None:
        pygame.draw.rect(self.screen, color, rect, border_width)
    
    def draw_straight_arrow(self, start: Tuple[int, int], end: Tuple[int, int], 
                          style: ConnectorStyle, double_ended: bool = False) -> None:
        """Draw a straight arrow between two points"""
        # Calculate direction vector
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length > 0:
            # Normalize direction
            dx, dy = dx/length, dy/length
            
            # Adjust start and end points to cell edges
            cell_radius = ElementStyle().width // 2  # Using default element width
            start_x = start[0] + dx * cell_radius
            start_y = start[1] + dy * cell_radius
            end_x = end[0] - dx * cell_radius
            end_y = end[1] - dy * cell_radius
            
            # Draw the line
            pygame.draw.line(self.screen, style.color, 
                           (start_x, start_y), (end_x, end_y), 
                           style.thickness)
            
            # Draw arrow heads - use positive direction for end arrow and negative for start arrow
            self._draw_arrow_head((end_x, end_y), (dx, dy), style)
            if double_ended:
                self._draw_arrow_head((start_x, start_y), (-dx, -dy), style)
    
    def draw_curved_arrow(self, start: Tuple[int, int], end: Tuple[int, int], 
                         style: ConnectorStyle, control_height: int = 100,
                         double_ended: bool = False) -> None:
        """Draw a curved arrow between two points"""
        # Move start and end points up to the top edge of cells
        cell_height = ElementStyle().height // 2
        start = (start[0], start[1] - cell_height)
        end = (end[0], end[1] - cell_height)
        
        # Calculate control point from the adjusted start/end points
        control_x = (start[0] + end[0]) / 2
        control_y = min(start[1], end[1]) - control_height
        control_point = (control_x, control_y)
        
        # Generate curve points
        points = []
        steps = 30
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control_point[0] + t**2 * end[0]
            y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control_point[1] + t**2 * end[1]
            points.append((int(x), int(y)))
        
        if len(points) > 1:
            # Draw the curve
            pygame.draw.lines(self.screen, style.color, False, points, style.thickness)
            
            if len(points) >= 2:
                # Draw arrow heads using the curve points directly (no additional height adjustment needed)
                end_dir = (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
                self._draw_arrow_head(points[-1], end_dir, style)
                
                if double_ended:
                    start_dir = (points[1][0] - points[0][0], points[1][1] - points[0][1])
                    self._draw_arrow_head(points[0], start_dir, style)
    
    def _draw_arrow_head(self, point: Tuple[int, int], direction: Tuple[float, float], 
                        style: ConnectorStyle) -> None:
        """Helper method to draw an arrow head"""
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            normalized = (direction[0]/length, direction[1]/length)
            
            left_point = (
                point[0] - normalized[0] * style.head_size - normalized[1] * style.head_size/2,
                point[1] - normalized[1] * style.head_size + normalized[0] * style.head_size/2
            )
            right_point = (
                point[0] - normalized[0] * style.head_size + normalized[1] * style.head_size/2,
                point[1] - normalized[1] * style.head_size - normalized[0] * style.head_size/2
            )
            
            pygame.draw.polygon(self.screen, style.color, [point, left_point, right_point])
    
    def update_display(self):
        pygame.display.flip()

class VideoWriter:
    """Handles saving frames and creating videos"""
    def __init__(self, output_dir: str = "frames"):
        self.frame_dir = output_dir
        self.frame_count = 0
        os.makedirs(output_dir, exist_ok=True)
    
    def save_frame(self, screen):
        pygame.image.save(screen, f"{self.frame_dir}/frame_{self.frame_count:04d}.png")
        self.frame_count += 1
    
    def create_video(self, output_filename: str = "animation.mp4", fps: int = 30):
        frames = sorted(glob.glob(f"{self.frame_dir}/frame_*.png"))
        if not frames:
            print("No frames found!")
            return
            
        frame = cv2.imread(frames[0])
        height, width, layers = frame.shape
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
        
        for frame_path in frames:
            video.write(cv2.imread(frame_path))
            
        video.release()

class DataStructureVisualizer(ABC, Generic[T]):
    """Abstract base class for data structure visualizers"""
    def __init__(self, config: Optional[BaseVisualizerConfig] = None):
        self.config = config or BaseVisualizerConfig()
        self.renderer = Renderer(self.config)
        self.video_writer = VideoWriter()
        self.element_style = ElementStyle()
        self.connector_style = ConnectorStyle()
        self.cells: List[Cell] = []
    
    @abstractmethod
    def create_cells(self, data_structure: T) -> List[Cell]:
        """Convert the data structure into a list of cells with proper positioning"""
        pass
    
    def draw_structure(self, data_structure: T, highlighted_elements: Optional[List[Any]] = None) -> None:
        """Draw the data structure in its current state"""
        self.renderer.clear_screen()
        
        # Create or update cells
        self.cells = self.create_cells(data_structure)
        
        # Update highlighting
        if highlighted_elements:
            for cell in self.cells:
                cell.highlighted = cell.value in highlighted_elements
        
        # Draw cells and their connections
        for cell in self.cells:
            self.renderer.draw_cell(cell, self.element_style)
            for connected_cell in cell.connections:
                self.renderer.draw_connection(cell, connected_cell, self.connector_style)
        
        self.renderer.update_display()
        self.video_writer.save_frame(self.renderer.screen)
    
    @abstractmethod
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        """Animate a data structure operation"""
        pass
    
    def create_video(self, output_filename: str = "animation.mp4", fps: int = 30):
        self.video_writer.create_video(output_filename, fps)
    
    def cleanup(self):
        pygame.quit()

class ArrayVisualizer(DataStructureVisualizer[List[int]]):
    """Concrete implementation for array visualization"""
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
    
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        if operation_name == "swap":
            self._animate_swap(*args, **kwargs)
        # Add more operations as needed
    
    def _animate_swap(self, array: List[int], idx1: int, idx2: int) -> List[int]:
        """Animate swapping two elements"""
        # Draw initial state
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        
        # Draw swap arrow with curved=True
        cell1 = self.cells[idx1]
        cell2 = self.cells[idx2]
        self.renderer.draw_connection(cell1, cell2, self.connector_style, curved=True, double_ended=True)
        
        self.renderer.update_display()
        self.video_writer.save_frame(self.renderer.screen)
        
        # Perform the swap
        array[idx1], array[idx2] = array[idx2], array[idx1]
        
        # Draw final state
        self.draw_structure(array, highlighted_elements=[array[idx1], array[idx2]])
        
        return array

class Node:
    """Basic Node class for LinkedList"""
    def __init__(self, value: int):
        self.value = value
        self.next: Optional['Node'] = None

class LinkedListOperation(ABC):
    """Abstract base class for LinkedList operations"""
    @abstractmethod
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, *args, **kwargs) -> Node:
        pass

class InsertOperation(LinkedListOperation):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, value: int, position: int) -> Node:
        """Animate inserting a node at a specific position"""
        # Show initial state
        visualizer.draw_structure(head)
        
        # Create new node
        new_node = Node(value)
        
        # Handle insertion at the beginning
        if position == 0:
            new_node.next = head
            head = new_node
            visualizer.draw_structure(head, highlighted_elements=[value])
            return head
        
        # Find insertion point
        current = head
        for i in range(position - 1):
            if current is None:
                return head
            current = current.next
        
        if current is None:
            return head
        
        # Perform insertion
        new_node.next = current.next
        current.next = new_node
        
        # Show final state
        visualizer.draw_structure(head, highlighted_elements=[value])
        return head

class DeleteOperation(LinkedListOperation):
    def animate(self, visualizer: 'LinkedListVisualizer', head: Node, position: int) -> Node:
        """Animate deleting a node at a specific position"""
        if not head:
            return None
        
        # Show initial state with highlighted node to be deleted
        current = head
        for i in range(position):
            if current:
                current = current.next
        
        if current:
            visualizer.draw_structure(head, highlighted_elements=[current.value])
        
        # Handle deletion at the beginning
        if position == 0:
            head = head.next
            visualizer.draw_structure(head)
            return head
        
        # Find node to delete
        current = head
        prev = None
        for i in range(position):
            if current is None:
                return head
            prev = current
            current = current.next
        
        if current is None:
            return head
        
        # Perform deletion
        prev.next = current.next
        
        # Show final state
        visualizer.draw_structure(head)
        return head

class LinkedListVisualizer(DataStructureVisualizer[Node]):
    """Concrete implementation for LinkedList visualization"""
    def __init__(self, config: Optional[BaseVisualizerConfig] = None):
        super().__init__(config)
        self.operations = {
            "insert": InsertOperation(),
            "delete": DeleteOperation()
        }

    def create_cells(self, head: Node) -> List[Cell]:
        cells = []
        current = head
        
        # Calculate total width needed
        node_count = 0
        temp = head
        while temp:
            node_count += 1
            temp = temp.next
        
        total_width = node_count * (self.element_style.width + self.element_style.spacing) - self.element_style.spacing
        start_x = (self.config.width - total_width) // 2
        y = self.config.height // 2 - self.element_style.height // 2
        
        # Create cells and connections
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
    
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        """Delegate animation to specific operation class"""
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")
        return self.operations[operation_name].animate(self, *args, **kwargs)

    def draw_structure(self, data_structure: Node, highlighted_elements: Optional[List[Any]] = None) -> None:
        """Override draw_structure to use straight arrows"""
        self.renderer.clear_screen()
        
        # Create or update cells
        self.cells = self.create_cells(data_structure)
        
        # Update highlighting
        if highlighted_elements:
            for cell in self.cells:
                cell.highlighted = cell.value in highlighted_elements
        
        # Draw cells and their connections
        for i in range(len(self.cells) - 1):  # Only draw connection to next cell
            cell = self.cells[i]
            next_cell = self.cells[i + 1]
            self.renderer.draw_cell(cell, self.element_style)
            self.renderer.draw_connection(cell, next_cell, self.connector_style, curved=False)
            
        # Draw the last cell (which has no forward connection)
        if self.cells:
            self.renderer.draw_cell(self.cells[-1], self.element_style)
        
        self.renderer.update_display()
        self.video_writer.save_frame(self.renderer.screen)

# Example usage
if __name__ == "__main__":
    visualizer = LinkedListVisualizer()
    
    # Create a sample linked list: 1 -> 3 -> 5 -> 7
    head = Node(1)
    head.next = Node(3)
    head.next.next = Node(5)
    head.next.next.next = Node(7)
    
    # Initial state
    visualizer.draw_structure(head)
    
    # Insert 4 at position 2
    head = visualizer.animate_operation("insert", head, 4, 2)
    
    # Delete node at position 1
    head = visualizer.animate_operation("delete", head, 1)
    
    # Create video and cleanup
    visualizer.create_video()
    visualizer.cleanup()