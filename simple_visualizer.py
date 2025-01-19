import pygame
import cv2
import os
import glob
import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from frame import Frame, DataStructure
from data_structures import Node

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
    element_spacing: int = width // 12  # Increased spacing between elements
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
        # For dictionary entries, draw as a simple text row
        if isinstance(value, tuple) and len(value) == 2:
            # Create text surfaces for key and value (without curly braces)
            key_surface = self.font.render(str(value[0]), True, self.config.text_color)
            separator_surface = self.font.render(": ", True, self.config.text_color)
            value_surface = self.font.render(str(value[1]), True, self.config.text_color)
            
            # Calculate total width needed
            total_width = (key_surface.get_width() + 
                         separator_surface.get_width() + value_surface.get_width())
            total_height = max(key_surface.get_height(), value_surface.get_height())
            
            # Create a rect for highlighting if needed
            rect = pygame.Rect(x, y, total_width + 20, total_height + 10)  # Add padding
            if highlighted:
                pygame.draw.rect(self.screen, self.config.highlight_color, rect, border_radius=5)
            
            # Draw the text components
            current_x = x + 10  # Start with padding
            text_y = y + (total_height - key_surface.get_height()) // 2 + 5
            
            self.screen.blit(key_surface, (current_x, text_y))
            current_x += key_surface.get_width()
            self.screen.blit(separator_surface, (current_x, text_y))
            current_x += separator_surface.get_width()
            self.screen.blit(value_surface, (current_x, text_y))
            
            return rect
            
        # For other types, keep existing box drawing logic
        rect = pygame.Rect(x, y, self.config.element_size, self.config.element_size)
        color = self.config.highlight_color if highlighted else self.config.element_color
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        if isinstance(value, Node):
            text_surface = self.font.render(str(value.value), True, self.config.text_color)
        else:
            text_surface = self.font.render(str(value), True, self.config.text_color)
            
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return rect
        
    def draw_arrow(self, start: Tuple[int, int], end: Tuple[int, int], curved: bool = True):
        """Draw an arrow between two points"""
        if curved and start != end:  # Only adjust height for curved arrows between different points
            # Adjust start and end points to be at the top edge
            start = (start[0], start[1] - self.config.element_size // 2)
            end = (end[0], end[1] - self.config.element_size // 2)
            
            control_y = min(start[1], end[1]) - 100
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
            # Use original points for straight arrows and self-arrows
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
            
        # Remove duplicates while preserving order
        unique_pointers = list(dict.fromkeys(pointers))
        
        # Create text surfaces
        text_surfaces = []
        total_height = 0
        
        # Create all text surfaces and calculate total height
        for pointer in unique_pointers:  # Use unique_pointers instead of pointers
            text_surface = self.font.render(pointer, True, self.config.pointer_color)
            text_surfaces.append(text_surface)
            total_height += text_surface.get_height()
        
        # Add spacing between texts
        total_height += (len(text_surfaces) - 1) * 50
        
        # Position text starting from top
        current_y = rect.top - 40 - total_height
        
        # Draw all text surfaces
        for text_surface in text_surfaces:
            text_rect = text_surface.get_rect(centerx=rect.centerx, top=current_y)
            self.screen.blit(text_surface, text_rect)
            current_y += text_surface.get_height() + 50
            
        # Draw single arrow for all text
        arrow_start = (rect.centerx, rect.top - 30)
        arrow_end = (rect.centerx, rect.top)
        self.draw_arrow(arrow_start, arrow_end, curved=False)
        
    def draw_structure(self, structure: DataStructure, base_y: int) -> List[pygame.Rect]:
        """Draw a single data structure (array or linked list)"""
        # Handle empty structure case
        if not structure.elements:
            text = "Empty Array" if structure.type == "array" else "Empty " + structure.type.capitalize()
            text_surface = self.font.render(text, True, self.config.text_color)
            text_rect = text_surface.get_rect(center=(self.config.width // 2, base_y))
            self.screen.blit(text_surface, text_rect)
            return []

        # Different spacing for different structure types
        spacing = 40 if structure.type == "linked_list" else 15  # Fixed 40px spacing for linked lists
        if structure.type == "dict":
            spacing = 25  # Slightly larger spacing for dictionaries
            
        num_elements = len(structure.elements)
        
        # Calculate element size to fit within available width
        available_width = self.config.width - 120  # Total width minus margins
        
        # For linked list or dictionary, calculate size for single nodes
        if structure.type in ["linked_list", "dict"]:
            element_size = min(
                (available_width - (num_elements - 1) * spacing) // num_elements,
                self.config.height // 4
            )
            total_width = num_elements * element_size + (num_elements - 1) * spacing
            
            # Add extra space for braces if it's a dictionary
            if structure.type == "dict":
                total_width += self.config.font_size * 2  # Space for left and right braces
        else:
            element_size = min(
                (available_width - (num_elements - 1) * spacing) // num_elements,
                self.config.height // 4
            )
            total_width = num_elements * element_size + (num_elements - 1) * spacing
        
        # Use position if provided, otherwise center horizontally
        if structure.position:
            start_x, y = structure.position
        else:
            start_x = (self.config.width - total_width) // 2
            y = base_y
            
        # Add extra left margin for dictionaries
        if structure.type == "dict":
            start_x = max(start_x, self.config.width // 10)  # Ensure minimum left margin
            
            # Draw opening brace with more spacing
            brace_surface = self.font.render("{ ", True, self.config.text_color)  # Note the space after {
            self.screen.blit(brace_surface, (start_x, y))
            start_x += brace_surface.get_width() + 20  # Add extra spacing after brace

        element_rects = []
        for i, value in enumerate(structure.elements):
            x = start_x + i * (element_size + spacing)
            rect = self.draw_element(value, x, y, i in structure.highlighted)
            element_rects.append(rect)
            
            if i in structure.labels:
                self.draw_labels(rect, structure.labels[i])
            if i in structure.pointers:
                self.draw_pointers(rect, structure.pointers[i])

        # Draw closing brace for dictionary with more spacing
        if structure.type == "dict" and element_rects:
            last_rect = element_rects[-1]
            brace_surface = self.font.render(" }", True, self.config.text_color)  # Note the space before }
            self.screen.blit(brace_surface, (last_rect.right + spacing, y))

        # Draw arrows for linked list
        if structure.type == "linked_list":
            is_doubly = getattr(structure, "is_doubly", False)
            
            # Draw regular linked list arrows
            for i in range(len(element_rects) - 1):
                from_rect = element_rects[i]
                to_rect = element_rects[i + 1]
                
                # Draw forward arrow
                start = (from_rect.right, from_rect.centery)
                end = (to_rect.left, to_rect.centery)
                self.draw_arrow(start, end, curved=False)
                
                # Draw backward arrow for doubly linked list
                if is_doubly:
                    start = (to_rect.left, to_rect.centery + 10)
                    end = (from_rect.right, from_rect.centery + 10)
                    self.draw_arrow(start, end, curved=False)
            
            # Draw self arrows (cycles)
            if structure.self_arrows:
                for idx in structure.self_arrows:
                    if 0 <= idx < len(element_rects):
                        rect = element_rects[idx]
                        # Draw straight arrow to top edge
                        start = (rect.centerx, rect.top - 30)
                        end = (rect.centerx, rect.top)
                        self.draw_arrow(start, end, curved=False)
        else:
            # For other structures (array and dict), keep center-to-center curved arrows
            for from_idx, to_idx in structure.arrows:
                if 0 <= from_idx < len(element_rects) and 0 <= to_idx < len(element_rects):
                    self.draw_arrow(
                        element_rects[from_idx].center,
                        element_rects[to_idx].center,
                        curved=True
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