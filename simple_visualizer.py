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
        text_rect = text_surface.get_rect(centerx=rect.centerx, bottom=rect.top - 45)
        self.screen.blit(text_surface, text_rect)
        
        
        arrow_start = (rect.centerx, text_rect.bottom + 10)
        arrow_end = (rect.centerx, rect.top)
        self.draw_arrow(arrow_start, arrow_end, curved=False)
        
    def draw_structure(self, structure: DataStructure, base_y: int) -> List[pygame.Rect]:
        """Draw a single data structure (array or linked list)"""
        # Handle empty structure case
        if not structure.elements:
            # Draw empty state message
            text = "Empty Array"
            text_surface = self.font.render(text, True, self.config.text_color)
            text_rect = text_surface.get_rect(center=(self.config.width // 2, base_y))
            self.screen.blit(text_surface, text_rect)
            return []

        # Fixed spacing of 15px between elements
        spacing = 15
        num_elements = len(structure.elements)
        
        # Calculate element size to make squares that fit within available width
        available_width = self.config.width - 200  # Total width minus margins
        spacing_total = spacing * (num_elements - 1)
        element_size = min(
            (available_width - spacing_total) // num_elements,  # Width-based size
            self.config.height // 4  # Height-based limit to prevent too large squares
        )
        
        total_width = num_elements * (element_size + spacing) - spacing
        
        # Use position if provided, otherwise center horizontally
        if structure.position:
            start_x, y = structure.position
        else:
            start_x = (self.config.width - total_width) // 2
            y = base_y
        
        element_rects = []
        for i, value in enumerate(structure.elements):
            x = start_x + i * (element_size + spacing)
            # Create square rect with dynamic size
            rect = pygame.Rect(x, y, element_size, element_size)
            color = self.config.highlight_color if i in structure.highlighted else self.config.element_color
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            
            text_surface = self.font.render(str(value), True, self.config.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
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
                
        # Draw self-arrows with increased spacing
        if structure.self_arrows:
            for idx in structure.self_arrows:
                if 0 <= idx < len(element_rects):
                    rect = element_rects[idx]
                    # Move text higher up
                    text_y = rect.top - 60
                    
                    if idx in structure.pointers:
                        pointer_text = " ".join(structure.pointers[idx])
                        text_surface = self.font.render(pointer_text, True, self.config.pointer_color)
                        text_rect = text_surface.get_rect(centerx=rect.centerx, bottom=text_y)
                        self.screen.blit(text_surface, text_rect)
                        
                        # Start arrow with increased gap from text
                        arrow_start = (rect.centerx, text_rect.bottom + 20)
                        self.draw_arrow(arrow_start, rect.center, curved=False)
                
        return element_rects
        
    def draw_variables(self, variables: Dict[str, Any], y: int):
        """Draw algorithm variables in a clean format"""
        if not variables:
            return
            
        x = self.config.width // 20  # Start from left margin
        for name, value in variables.items():
            text = f"{name} = {value}"
            text_surface = self.font.render(text, True, self.config.text_color)
            text_rect = text_surface.get_rect(left=x, top=y)
            self.screen.blit(text_surface, text_rect)
            y += text_rect.height + 5  # Add some spacing between variables
            
    def draw_frame(self, frame: Frame):
        """Draw a complete frame with multiple data structures"""
        
        self.screen.fill(self.config.background_color)
        
        # Draw variables at the top
        if frame.variables:
            self.draw_variables(frame.variables, self.config.height // 8)
        
        # Adjust base_y to account for variables
        base_y_offset = self.config.height // 4
        if frame.variables:
            base_y_offset += len(frame.variables) * (self.config.font_size + 5)
            
        # Draw each structure
        for name, structure in frame.structures.items():
            self.draw_structure(structure, base_y_offset)
            base_y_offset += self.config.vertical_spacing
            
        # Draw frame text at the middle/bottom
        if frame.text:
            # Position text in middle (3/4 of height) or bottom (7/8 of height)
            text_y = int(self.config.height * 0.75)  # Default to middle
            
            text_rect = pygame.Rect(
                60,  # 60px padding on left
                text_y - self.config.height//12,  # Center the rect around the y position
                self.config.width - 120,  # 60px padding on each side
                self.config.height//6  # Taller rect for wrapped text
            )
            pygame.draw.rect(self.screen, (245, 245, 245), text_rect, border_radius=20)
            self.drawText(
                self.screen,
                frame.text,
                self.config.text_color,
                text_rect,
                self.font,
                aa=True
            )
            
        # Save the frame
        pygame.image.save(self.screen, f"frames/frame_{self.frame_count:04d}.png")
        self.frame_count += 1
        
    def drawText(self, surface, text, color, rect, font, aa=False, bkg=None):
        y = rect.top + 10  # Add some padding at the top
        line_spacing = font.get_height() * 0.5  # Increase line spacing to 50% of font height

        # get the height of the font
        font_height = font.size("Tg")[1]

        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + font_height > rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width - 40 and i < len(text):  # More padding
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)

            surface.blit(image, (rect.left + 20, y))  # More left padding
            y += font_height + line_spacing  # Add the increased line spacing

            # remove the text we just blitted
            text = text[i:]

        return text
        
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