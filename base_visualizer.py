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
    
    def save_frame(self, hold_time: float = 0) -> None:
        """Save the current frame, optionally holding it for the specified duration"""
        # Save the frame for the duration specified by hold_time
        frames = int(hold_time * 30)  # Assuming 30fps
        for _ in range(frames):
            self.video_writer.save_frame(self.renderer.screen)

    @abstractmethod
    def create_cells(self, data_structure: T) -> List[Cell]:
        """Convert the data structure into a list of cells with proper positioning"""
        pass
    
    def draw_structure(self, data_structure: T, highlighted_elements: Optional[List[Any]] = None, hold_time: float = 0) -> None:
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
        self.save_frame(hold_time)
    
    @abstractmethod
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        """Animate a data structure operation"""
        pass
    
    def create_video(self, output_filename: str = "animation.mp4", fps: int = 30):
        self.video_writer.create_video(output_filename, fps)
    
    def cleanup(self):
        pygame.quit() 