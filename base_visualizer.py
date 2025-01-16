from abc import ABC, abstractmethod
from dataclasses import dataclass
import pygame
import cv2
import os
import glob
import math
from typing import List, Dict, Optional, Tuple, Any, Generic, TypeVar, Set

T = TypeVar('T')

@dataclass
class BaseVisualizerConfig:
    width: int = 1080
    height: int = 1920
    
    background_color: Tuple[int, int, int] = (255, 255, 255)
    text_color: Tuple[int, int, int] = (0, 0, 0)
    
    visualization_height: float = 0.50
    transcript_height: float = 0.15
    code_height: float = 0.35
    
    font_size: int = height // 35
    code_font_size: int = height // 45
    
    animation_frames: int = 30
    
    default_x: int = width // 2
    default_y: int = int(height * 0.25)
    
    code_x: int = width // 15
    code_y: int = int(height * 0.65)
    code_line_height: int = height // 22
    code_highlight_color: Tuple[int, int, int] = (255, 240, 200)
    
    transcript_y: int = int(height * 0.57)
    
    max_elements_horizontal: int = 8

@dataclass
class ElementStyle:
    base_size: int = 1080 // 8
    
    width: int = base_size
    height: int = base_size
    min_size: int = base_size // 3
    spacing: int = base_size // 3
    
    color: Tuple[int, int, int] = (100, 100, 100)
    highlight_color: Tuple[int, int, int] = (255, 200, 200)
    
    def adjust_for_count(self, element_count: int, max_width: int, is_single_structure: bool = True) -> None:
        target_size = self.base_size
        
        if not is_single_structure:
            target_size = self.base_size // 2
        
        self.width = target_size
        self.height = target_size
        self.spacing = target_size // 3
        
        total_width = element_count * (self.width + self.spacing) - self.spacing
        
        if total_width > max_width * 0.9:
            available_width = max_width * 0.9
            new_size = max(
                self.min_size,
                int((available_width - (element_count - 1) * self.spacing) / element_count)
            )
            self.width = new_size
            self.height = new_size
            self.spacing = max(new_size // 4, 10)

@dataclass
class ConnectorStyle:
    color: Tuple[int, int, int] = (0, 100, 200)
    thickness: int = 3
    head_size: int = 15

class Cell:
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
        self.connections.add(other)
        other.connections.add(self)
    
    def disconnect_from(self, other: 'Cell') -> None:
        self.connections.discard(other)
        other.connections.discard(self)

class VideoWriter:
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

class Renderer:
    def __init__(self, config: BaseVisualizerConfig, video_writer: VideoWriter):
        self.config = config
        self.screen = pygame.Surface((config.width, config.height))
        self.font = pygame.font.Font(None, config.font_size)
        self.code_font = pygame.font.Font(None, config.code_font_size)
        self.video_writer = video_writer
        self.code_lines: List[str] = []
        self.highlighted_lines: Set[int] = set()
        self.line_comments: Dict[int, str] = {}
        self.transcript_text: str = ""
    
    def set_code(self, code: str) -> None:
        self.code_lines = code.strip().split('\n')
    
    def set_highlighted_lines(self, line_numbers: List[int]) -> None:
        self.highlighted_lines = set(line_numbers)
    
    def highlight_code_line(self, line_num: int, comment: str = "") -> None:
        self.highlighted_lines.add(line_num)
        if comment:
            self.line_comments[line_num] = comment
        self.draw_code()
    
    def set_transcript(self, text: str) -> None:
        self.transcript_text = text
    
    def draw_transcript(self) -> None:
        if self.transcript_text:
            transcript_height = self.config.height // 12
            transcript_rect = pygame.Rect(
                0,
                self.config.transcript_y - transcript_height//2,
                self.config.width,
                transcript_height
            )
            
            pygame.draw.rect(self.screen, (245, 245, 245), transcript_rect, border_radius=20)
            
            words = self.transcript_text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                test_surface = self.font.render(' '.join(current_line), True, self.config.text_color)
                if test_surface.get_width() > self.config.width * 0.85:
                    current_line.pop()
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            line_height = self.config.font_size * 1.2
            start_y = self.config.transcript_y - (len(lines) * line_height) / 2
            
            for i, line in enumerate(lines):
                self.draw_text(
                    line,
                    (self.config.width//2, start_y + i * line_height),
                    center=True,
                    font=self.font
                )
    
    def draw_code(self) -> None:
        if not self.code_lines:
            return
        
        code_section_height = len(self.code_lines) * self.config.code_line_height + 80
        code_bg = pygame.Rect(
            0,
            self.config.code_y - 40,
            self.config.width,
            code_section_height
        )
        pygame.draw.rect(self.screen, (245, 245, 245), code_bg)
        
        for i, line in enumerate(self.code_lines, start=1):
            y_pos = self.config.code_y + (i-1) * self.config.code_line_height
            
            if i in self.highlighted_lines:
                highlight_rect = pygame.Rect(
                    self.config.code_x - 10,
                    y_pos - self.config.code_line_height//3,
                    self.config.width - 2 * self.config.code_x + 20,
                    self.config.code_line_height
                )
                pygame.draw.rect(self.screen, self.config.code_highlight_color, highlight_rect)
            
            text_surface = self.code_font.render(line, True, self.config.text_color)
            self.screen.blit(text_surface, (self.config.code_x, y_pos))
            
            if i in self.line_comments:
                comment_surface = self.code_font.render(
                    self.line_comments[i],
                    True,
                    (100, 100, 100)
                )
                comment_x = self.config.code_x + text_surface.get_width() + 20
                self.screen.blit(comment_surface, (comment_x, y_pos))
    
    def clear_screen(self):
        self.screen.fill(self.config.background_color)
        self.draw_code()
        self.draw_transcript()
    
    def draw_text(self, text: str, position: Tuple[int, int], center: bool = True, font: Optional[pygame.font.Font] = None) -> pygame.Rect:
        font = font or self.font
        text_surface = font.render(text, True, self.config.text_color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_cell(self, cell: Cell, style: ElementStyle) -> None:
        pygame.draw.rect(
            self.screen,
            style.highlight_color if cell.highlighted else style.color,
            cell.rect,
            border_radius=10
        )
        self.draw_text(str(cell.value), cell.center)
    
    def draw_connection(self, start_cell: Cell, end_cell: Cell, 
                       style: ConnectorStyle, curved: bool = True,
                       double_ended: bool = False) -> None:
        if curved:
            self.draw_curved_arrow(start_cell.center, end_cell.center, style, double_ended=double_ended)
        else:
            self.draw_straight_arrow(start_cell.center, end_cell.center, style, double_ended=double_ended)
    
    def draw_rect(self, rect: pygame.Rect, color: Tuple[int, int, int], 
                 border_width: int = 0) -> None:
        pygame.draw.rect(self.screen, color, rect, border_width)
    
    def draw_straight_arrow(self, start: Tuple[int, int], end: Tuple[int, int], 
                          style: ConnectorStyle, double_ended: bool = False) -> None:
        pygame.draw.line(self.screen, style.color, start, end, style.thickness)
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        
        if length > 0:
            direction = (dx / length, dy / length)
            self._draw_arrow_head(end, (-direction[0], -direction[1]), style)
            
            if double_ended:
                self._draw_arrow_head(start, direction, style)
    
    def draw_curved_arrow(self, start: Tuple[int, int], end: Tuple[int, int], 
                         style: ConnectorStyle, control_height: int = 100,
                         double_ended: bool = False) -> None:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        control_point = (
            (start[0] + end[0]) // 2,
            min(start[1], end[1]) - control_height
        )
        
        points = []
        steps = 30
        
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control_point[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control_point[1] + t**2 * end[1]
            points.append((int(x), int(y)))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, style.color, False, points, style.thickness)
            
            end_direction = (
                points[-1][0] - points[-2][0],
                points[-1][1] - points[-2][1]
            )
            length = math.sqrt(end_direction[0]**2 + end_direction[1]**2)
            if length > 0:
                end_direction = (end_direction[0]/length, end_direction[1]/length)
                self._draw_arrow_head(points[-1], (-end_direction[0], -end_direction[1]), style)
                
                if double_ended:
                    start_direction = (
                        points[1][0] - points[0][0],
                        points[1][1] - points[0][1]
                    )
                    length = math.sqrt(start_direction[0]**2 + start_direction[1]**2)
                    if length > 0:
                        start_direction = (start_direction[0]/length, start_direction[1]/length)
                        self._draw_arrow_head(points[0], start_direction, style)
    
    def _draw_arrow_head(self, point: Tuple[int, int], direction: Tuple[float, float], 
                        style: ConnectorStyle) -> None:
        perpendicular = (-direction[1], direction[0])
        
        left_point = (
            int(point[0] + style.head_size * (-direction[0] + 0.5 * perpendicular[0])),
            int(point[1] + style.head_size * (-direction[1] + 0.5 * perpendicular[1]))
        )
        
        right_point = (
            int(point[0] + style.head_size * (-direction[0] - 0.5 * perpendicular[0])),
            int(point[1] + style.head_size * (-direction[1] - 0.5 * perpendicular[1]))
        )
        
        pygame.draw.polygon(self.screen, style.color, [point, left_point, right_point])
    
    def draw_self_pointing_arrow(self, center: Tuple[int, int], style: ConnectorStyle) -> None:
        # Draw an arc above the cell that points downward
        offset_y = -30  # Move up from the cell center
        width = 30      # Width of the arc
        height = 20     # Height of the arc
        
        # Calculate control points for the arc
        start_point = (center[0] - width//2, center[1] + offset_y)
        control_point = (center[0], center[1] + offset_y - height)
        end_point = (center[0] + width//2, center[1] + offset_y)
        
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve
            x = (1-t)**2 * start_point[0] + 2*(1-t)*t * control_point[0] + t**2 * end_point[0]
            y = (1-t)**2 * start_point[1] + 2*(1-t)*t * control_point[1] + t**2 * end_point[1]
            points.append((int(x), int(y)))
        
        # Draw the arc
        if len(points) > 1:
            pygame.draw.lines(self.screen, style.color, False, points, style.thickness)
            
            # Draw arrow head pointing down to the cell
            arrow_point = (center[0], center[1] - 5)  # Slightly above cell center
            self._draw_arrow_head(arrow_point, (0, 1), style)  # Point downward
    
    def update_display(self):
        pass

class DataStructureVisualizer(ABC, Generic[T]):
    def __init__(self, config: Optional[BaseVisualizerConfig] = None):
        self.config = config or BaseVisualizerConfig()
        self.video_writer = VideoWriter()
        self.renderer = Renderer(self.config, self.video_writer)
        self.cells: List[Cell] = []
        self.current_frame = 0
    
    def set_solution_code(self, code: str) -> None:
        self.renderer.set_code(code)
        self.renderer.clear_screen()
        self.renderer.video_writer.save_frame(self.renderer.screen)
    
    def highlight_code_lines(self, line_numbers: List[int], hold_time: float = 0) -> None:
        self.renderer.set_highlighted_lines(line_numbers)
        self.renderer.clear_screen()
        self.save_frame(hold_time)
    
    def draw_current_state(self) -> None:
        self.renderer.clear_screen()
        for cell in self.cells:
            self.renderer.draw_cell(cell, ElementStyle())
            for connected_cell in cell.connections:
                if connected_cell in self.cells:
                    self.renderer.draw_connection(cell, connected_cell, ConnectorStyle())
    
    def save_frame(self, hold_time: float = 0) -> None:
        frames_to_hold = int(hold_time * 30)
        for _ in range(max(1, frames_to_hold)):
            self.renderer.video_writer.save_frame(self.renderer.screen)
            self.current_frame += 1
    
    def draw_structure(self, data_structure: T, highlighted_elements: Optional[List[Any]] = None, hold_time: float = 0) -> None:
        self.cells = self.create_cells(data_structure)
        
        if highlighted_elements:
            for cell in self.cells:
                if cell.value in highlighted_elements:
                    cell.highlighted = True
        
        self.draw_current_state()
        self.save_frame(hold_time)
    
    @abstractmethod
    def create_cells(self, data_structure: T) -> List[Cell]:
        pass
    
    @abstractmethod
    def animate_operation(self, operation_name: str, *args, **kwargs) -> None:
        pass
    
    def create_video(self, output_filename: str = "animation.mp4", fps: int = 30):
        self.video_writer.create_video(output_filename, fps)
    
    def cleanup(self):
        for file in glob.glob("frames/*.png"):
            os.remove(file)

class DataStructureState:
    def __init__(self):
        self.elements: List[Any] = []
        self.positions: Dict[int, Tuple[int, int]] = {}
        self.highlighted: List[int] = []
        self.arrows: List[Tuple[int, int]] = []
    
    def interpolate(self, target_state: 'DataStructureState', progress: float) -> 'DataStructureState':
        result = DataStructureState()
        result.elements = target_state.elements.copy()
        result.highlighted = target_state.highlighted.copy()
        result.arrows = target_state.arrows.copy()
        
        for i in self.positions:
            if i in target_state.positions:
                start_pos = self.positions[i]
                end_pos = target_state.positions[i]
                result.positions[i] = (
                    int(start_pos[0] + (end_pos[0] - start_pos[0]) * progress),
                    int(start_pos[1] + (end_pos[1] - start_pos[1]) * progress)
                )
            else:
                result.positions[i] = self.positions[i]
        
        for i in target_state.positions:
            if i not in self.positions:
                result.positions[i] = target_state.positions[i]
        
        return result 