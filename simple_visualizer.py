import pygame
import cv2
import os
import glob
import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from frame import Frame, DataStructure

@dataclass
class VisualizerConfig:
    """Configuration for the visualizer"""
    width: int = 1080
    height: int = 1920
    background_color: Tuple[int, int, int] = (255, 255, 255)
    text_color: Tuple[int, int, int] = (0, 0, 0)
    element_color: Tuple[int, int, int] = (100, 100, 100)
    highlight_color: Tuple[int, int, int] = (255, 200, 200)
    arrow_color: Tuple[int, int, int] = (0, 100, 200)
    pointer_color: Tuple[int, int, int] = (50, 50, 200)
    label_color: Tuple[int, int, int] = (100, 100, 100)
    font_size: int = height // 35
    element_size: int = width // 8
    element_spacing: int = width // 24
    vertical_spacing: int = height // 8  

class SimpleVisualizer:
    def __init__(self, config: Optional[VisualizerConfig] = None):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()
        
        self.config = config or VisualizerConfig()
        self.screen = pygame.Surface((self.config.width, self.config.height))
        self.font = pygame.font.Font(None, self.config.font_size)
        
        
        os.makedirs("frames", exist_ok=True)
        for f in glob.glob("frames/*.png"):
            os.remove(f)
            
        self.frame_count = 0
        
    def draw_element(self, value: Any, x: int, y: int, highlighted: bool = False) -> pygame.Rect:
        """Draw a single element (box with value)"""
        rect = pygame.Rect(x, y, self.config.element_size, self.config.element_size)
        color = self.config.highlight_color if highlighted else self.config.element_color
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        
        text_surface = self.font.render(str(value), True, self.config.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return rect
        
    def draw_arrow(self, start: Tuple[int, int], end: Tuple[int, int], curved: bool = True):
        """Draw an arrow between two points"""
        if curved:
            
            control_y = min(start[1], end[1]) - 50
            control_point = ((start[0] + end[0]) // 2, control_y)
            
            points = []
            steps = 30
            for i in range(steps + 1):
                t = i / steps
                x = (1-t)**2 * start[0] + 2*(1-t)*t * control_point[0] + t**2 * end[0]
                y = (1-t)**2 * start[1] + 2*(1-t)*t * control_point[1] + t**2 * end[1]
                points.append((int(x), int(y)))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.config.arrow_color, False, points, 2)
                
                
                dx = points[-1][0] - points[-2][0]
                dy = points[-1][1] - points[-2][1]
                angle = math.atan2(dy, dx)
                
                head_length = 15
                head_angle = math.pi / 6
                
                pygame.draw.polygon(self.screen, self.config.arrow_color, [
                    points[-1],
                    (points[-1][0] - head_length * math.cos(angle + head_angle),
                     points[-1][1] - head_length * math.sin(angle + head_angle)),
                    (points[-1][0] - head_length * math.cos(angle - head_angle),
                     points[-1][1] - head_length * math.sin(angle - head_angle))
                ])
        else:
            
            pygame.draw.line(self.screen, self.config.arrow_color, start, end, 2)
            
            
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            angle = math.atan2(dy, dx)
            
            head_length = 15
            head_angle = math.pi / 6
            
            pygame.draw.polygon(self.screen, self.config.arrow_color, [
                end,
                (end[0] - head_length * math.cos(angle + head_angle),
                 end[1] - head_length * math.sin(angle + head_angle)),
                (end[0] - head_length * math.cos(angle - head_angle),
                 end[1] - head_length * math.sin(angle - head_angle))
            ])
            
    def draw_self_arrow(self, center: Tuple[int, int]):
        """Draw an arrow that points to itself"""
        radius = 20
        start_angle = -math.pi/2
        end_angle = math.pi/2
        
        points = []
        steps = 20
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * (i / steps)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((int(x), int(y)))
            
        if len(points) > 1:
            pygame.draw.lines(self.screen, self.config.arrow_color, False, points, 2)
            
            
            pygame.draw.polygon(self.screen, self.config.arrow_color, [
                (center[0], center[1] + 5),
                (center[0] - 5, center[1] - 5),
                (center[0] + 5, center[1] - 5)
            ])
            
    def draw_labels(self, rect: pygame.Rect, labels: List[str]):
        """Draw labels below an element"""
        y = rect.bottom + 5
        for label in labels:
            text_surface = self.font.render(label, True, self.config.label_color)
            text_rect = text_surface.get_rect(centerx=rect.centerx, top=y)
            self.screen.blit(text_surface, text_rect)
            y += text_rect.height + 2
            
    def draw_pointers(self, rect: pygame.Rect, pointers: List[str]):
        """Draw pointers above an element"""
        if not pointers:
            return
            
        
        pointer_text = " ".join(pointers)
        text_surface = self.font.render(pointer_text, True, self.config.pointer_color)
        text_rect = text_surface.get_rect(centerx=rect.centerx, bottom=rect.top - 5)
        self.screen.blit(text_surface, text_rect)
        
        
        arrow_start = (rect.centerx, text_rect.bottom)
        arrow_end = (rect.centerx, rect.top)
        self.draw_arrow(arrow_start, arrow_end, curved=False)
        
    def draw_structure(self, structure: DataStructure, base_y: int) -> List[pygame.Rect]:
        """Draw a single data structure (array or linked list)"""
        total_width = len(structure.elements) * (self.config.element_size + self.config.element_spacing) - self.config.element_spacing
        
        
        if structure.position:
            start_x, y = structure.position
        else:
            start_x = (self.config.width - total_width) // 2
            y = base_y
        
        
        element_rects = []
        for i, value in enumerate(structure.elements):
            x = start_x + i * (self.config.element_size + self.config.element_spacing)
            rect = self.draw_element(value, x, y, i in structure.highlighted)
            element_rects.append(rect)
            
            
            if i in structure.labels:
                self.draw_labels(rect, structure.labels[i])
            if i in structure.pointers:
                self.draw_pointers(rect, structure.pointers[i])
                
        
        for from_idx, to_idx in structure.arrows:
            if 0 <= from_idx < len(element_rects) and 0 <= to_idx < len(element_rects):
                
                curved = structure.type != "linked_list"
                self.draw_arrow(
                    element_rects[from_idx].center,
                    element_rects[to_idx].center,
                    curved=curved
                )
                
        
        for idx in structure.self_arrows:
            if 0 <= idx < len(element_rects):
                self.draw_self_arrow(element_rects[idx].center)
                
        return element_rects
        
    def draw_frame(self, frame: Frame):
        """Draw a complete frame with multiple data structures"""
        
        self.screen.fill(self.config.background_color)
        
        
        num_structures = len(frame.structures)
        if num_structures == 1:
            
            base_y = self.config.height // 4
            for structure in frame.structures.values():
                self.draw_structure(structure, base_y)
        else:
            
            start_y = self.config.height // 6
            spacing = self.config.vertical_spacing
            for i, structure in enumerate(frame.structures.values()):
                base_y = start_y + i * spacing
                self.draw_structure(structure, base_y)
                
        
        if frame.text:
            text_surface = self.font.render(frame.text, True, self.config.text_color)
            text_rect = text_surface.get_rect(center=(self.config.width//2, self.config.height*3//4))
            self.screen.blit(text_surface, text_rect)
            
        
        pygame.image.save(self.screen, f"frames/frame_{self.frame_count:04d}.png")
        self.frame_count += 1
        
    def create_video(self, output_filename: str = "animation.mp4", fps: int = 30):
        """Create video from saved frames"""
        frames = sorted(glob.glob("frames/frame_*.png"))
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
        
        
        for f in frames:
            os.remove(f)
            
    def visualize_frames(self, frames: List[Frame], output_file: str = "animation.mp4"):
        """Main method to visualize a sequence of frames"""
        for frame in frames:
            
            if not hasattr(frame, 'structures'):
                frame = Frame.from_array(frame.elements, **{
                    k: v for k, v in frame.__dict__.items() 
                    if k != 'elements'
                })
            
            
            duration_seconds = float(frame.duration.rstrip('s'))
            num_frames = int(duration_seconds * 30)  
            
            for _ in range(num_frames):
                self.draw_frame(frame)
                
        self.create_video(output_file) 