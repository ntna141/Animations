import pygame
import cv2
import os
import glob
import math
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from frame import Frame, DataStructure
from data_structures import Node, TreeNode

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
        
        # Load and process the cat video
        self.cat_video = cv2.VideoCapture('cat.mp4')
        self.cat_frame_count = int(self.cat_video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.cat_current_frame = 0
        
        # Define the size for the overlay video (adjust as needed)
        self.overlay_width = 400  # pixels
        self.overlay_height = 300  # pixels
        
        os.makedirs("frames", exist_ok=True)
        for f in glob.glob("frames/*.png"):
            os.remove(f)
            
        self.frame_count = 0
        
    def process_video_frame(self):
        """Process a single frame of the cat video, removing green screen"""
        if self.cat_current_frame >= self.cat_frame_count:
            self.cat_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.cat_current_frame = 0
            
        ret, frame = self.cat_video.read()
        if not ret:
            return None
            
        self.cat_current_frame += 1
        
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame to desired overlay size
        frame = cv2.resize(frame, (self.overlay_width, self.overlay_height))
        
        # More generous green screen values
        lower_green = np.array([55, 130, 130])  # More specific to bright green
        upper_green = np.array([65, 255, 255])  # Narrower hue range
        
        # Convert frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        # Create mask
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Replace green areas with white
        frame[mask > 0] = [255, 255, 255]  # Set green pixels to white
        
        # Convert to pygame surface
        result = np.transpose(frame, (1, 0, 2))
        return pygame.surfarray.make_surface(result)

    def draw_element(self, value: Any, x: int, y: int, highlighted: bool = False) -> pygame.Rect:
        """Draw a single element (box with value)"""
        # For dictionary entries or set elements, draw as a simple text row
        if isinstance(value, tuple) and len(value) == 2:
            # Create text surfaces for key and value
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
        elif isinstance(value, (Node, TreeNode)):
            # For linked list nodes and tree nodes, draw boxes
            rect = pygame.Rect(x, y, self.config.element_size, self.config.element_size)
            color = self.config.highlight_color if highlighted else (255, 255, 255)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, border_radius=10, width=2)
            
            text_surface = self.font.render(str(value.value), True, self.config.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
            return rect
        else:
            # For set elements and other types, draw as simple text
            text_surface = self.font.render(str(value), True, self.config.text_color)
            total_height = text_surface.get_height()
            
            # Create a rect for highlighting if needed
            rect = pygame.Rect(x, y, text_surface.get_width() + 20, total_height + 10)  # Add padding
            if highlighted:
                pygame.draw.rect(self.screen, self.config.highlight_color, rect, border_radius=5)
            
            # Draw the text
            text_y = y + 5  # Add small padding
            self.screen.blit(text_surface, (x + 10, text_y))
            
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
        # Join all labels with spaces and render as one line
        text = " ".join(labels)
        text_surface = self.font.render(text, True, self.config.label_color)
        text_rect = text_surface.get_rect(centerx=rect.centerx, top=y)
        self.screen.blit(text_surface, text_rect)
        
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
        
    def get_node_at_index(self, root: TreeNode, node_idx: int) -> Optional[TreeNode]:
        """Get the node at a given index in the binary tree
        
        Args:
            root: Root node of the tree
            node_idx: Index of the node to find (0-based)
            
        Returns:
            The node at the given index, or None if not found
        """
        if node_idx == 0:
            return root
            
        # Calculate path to node
        path = []
        temp_idx = node_idx
        while temp_idx > 0:
            path.append(temp_idx % 2)  # 0 for left, 1 for right
            temp_idx = (temp_idx - 1) // 2
        path.reverse()
        
        # Follow path to node
        current = root
        for direction in path:
            if current is None:
                return None
            current = current.right if direction else current.left
            
        return current
        
    def collect_nodes_by_level(self, root: TreeNode, level: int = 0, node_idx: int = 0, 
                               nodes_by_level: Dict[int, List[Tuple[int, TreeNode]]] = None) -> Dict[int, List[Tuple[int, TreeNode]]]:
        """Collect all nodes in the tree by level, including their indices
        
        Args:
            root: Root node of the tree
            level: Current level
            node_idx: Current node's index in the tree
            nodes_by_level: Dictionary mapping level to list of (index, node) pairs
            
        Returns:
            Dictionary mapping level to list of (index, node) pairs
        """
        if nodes_by_level is None:
            nodes_by_level = {}
            
        if not root:
            return nodes_by_level
            
        if level not in nodes_by_level:
            nodes_by_level[level] = []
            
        # Store node with its tree index
        nodes_by_level[level].append((node_idx, root))
        
        # Process children with their correct indices
        if root.left:
            self.collect_nodes_by_level(root.left, level + 1, 2*node_idx + 1, nodes_by_level)
        if root.right:
            self.collect_nodes_by_level(root.right, level + 1, 2*node_idx + 2, nodes_by_level)
            
        return nodes_by_level
        
    def draw_tree(self, root: TreeNode, x: int, y: int, level_width: int, highlighted: List[int], 
                  labels: Dict[int, List[str]], pointers: Dict[int, List[str]], node_idx: int = 0, level: int = 0) -> List[pygame.Rect]:
        """Draw a binary tree recursively"""
        if not root:
            return []
            
        # Use fixed node size of 70px
        self.config.element_size = 70
            
        # First collect all nodes by level with their tree indices
        nodes_by_level = self.collect_nodes_by_level(root)
        rect_map = {}  # Will store node_idx to rect mapping
        all_rects = []
        
        # Calculate the maximum number of possible nodes at each level
        max_nodes_at_level = {level: 2**level for level in range(len(nodes_by_level))}
        
        # Draw each level
        for level, nodes in sorted(nodes_by_level.items()):
            if not nodes:
                continue
                
            # Calculate level width based on maximum possible nodes at this level
            level_width = self.config.width - 120  # Leave margins
            node_spacing = level_width / max_nodes_at_level[level]
            
            # Draw nodes at this level
            for node_idx, node in nodes:
                # Calculate position based on node's index in complete tree
                relative_pos = node_idx - (2**level - 1)  # Position within level
                node_x = 60 + node_spacing * relative_pos + node_spacing/2 - self.config.element_size/2
                node_y = y + level * self.config.vertical_spacing * 0.8
                
                # Draw node
                rect = self.draw_element(node, node_x, node_y, node_idx in highlighted)
                rect_map[node_idx] = rect
                all_rects.append(rect)
                
                # Draw labels and pointers
                if node_idx in labels:
                    self.draw_labels(rect, labels[node_idx])
                if node_idx in pointers:
                    self.draw_pointers(rect, pointers[node_idx])
                    
                # Draw connection to parent (except for root)
                if level > 0:
                    parent_idx = (node_idx - 1) // 2
                    if parent_idx in rect_map:
                        parent_rect = rect_map[parent_idx]
                        pygame.draw.line(self.screen, self.config.arrow_color,
                                       parent_rect.midbottom, rect.midtop, 2)
        
        return all_rects
        
    def get_tree_width_by_level(self, root: TreeNode, level: int = 0, width_by_level: Dict[int, int] = None) -> Dict[int, int]:
        """Calculate number of nodes at each level of the tree
        
        Args:
            root: Root node of the tree
            level: Current level
            width_by_level: Dictionary tracking number of nodes at each level
            
        Returns:
            Dictionary mapping level to number of nodes at that level
        """
        if width_by_level is None:
            width_by_level = {}
            
        if not root:
            return width_by_level
            
        width_by_level[level] = width_by_level.get(level, 0) + 1
        
        if root.left:
            self.get_tree_width_by_level(root.left, level + 1, width_by_level)
        if root.right:
            self.get_tree_width_by_level(root.right, level + 1, width_by_level)
            
        return width_by_level
        
    def draw_structure(self, structure: DataStructure, base_y: int) -> List[pygame.Rect]:
        """Draw a single data structure (array, linked list, or tree)"""
        # Handle empty structure case
        if not structure.elements:
            text = "Empty " + structure.type.capitalize()
            text_surface = self.font.render(text, True, self.config.text_color)
            text_rect = text_surface.get_rect(center=(self.config.width // 2, base_y))
            self.screen.blit(text_surface, text_rect)
            return []
            
        # Handle tree structure
        if structure.type == "tree":
            root = structure.elements
            if not root:
                return []
                
            # Calculate width needed for each level
            width_by_level = self.get_tree_width_by_level(root)
            max_width = max(width_by_level.values())
            
            # Calculate element size similar to array calculation
            available_width = self.config.width - 120  # Total width minus margins
            min_spacing = 20  # Minimum spacing between nodes
            element_size = min(
                (available_width - (max_width - 1) * min_spacing) // max_width,
                60  # Maximum size of 60px
            )
            
            # Store original element size
            original_element_size = self.config.element_size
            # Temporarily set element size for tree
            self.config.element_size = element_size
                
            # Calculate initial position for root
            start_x = self.config.width // 2
            y = self.config.height // 6
            initial_width = self.config.width // 2.5
            
            # Draw tree recursively
            element_rects = self.draw_tree(
                root, start_x, y, initial_width,
                structure.highlighted or [],
                structure.labels or {},
                structure.pointers or {}
            )
            
            # Draw any additional arrows between nodes
            for from_idx, to_idx in structure.arrows or []:
                if 0 <= from_idx < len(element_rects) and 0 <= to_idx < len(element_rects):
                    self.draw_arrow(
                        element_rects[from_idx].center,
                        element_rects[to_idx].center,
                        curved=True
                    )
                    
            # Draw any self arrows
            for idx in structure.self_arrows or []:
                if 0 <= idx < len(element_rects):
                    rect = element_rects[idx]
                    start = (rect.centerx, rect.top - 30)
                    end = (rect.centerx, rect.top)
                    self.draw_arrow(start, end, curved=False)
            
            # Restore original element size
            self.config.element_size = original_element_size
                    
            return element_rects

        # Different spacing for different structure types
        spacing = 40 if structure.type == "linked_list" else 15  # Fixed 40px spacing for linked lists
        if structure.type in ["dict", "set"]:
            spacing = 25  # Slightly larger spacing for dictionaries and sets
            
        num_elements = len(structure.elements)
        
        # Calculate element size to fit within available width
        available_width = self.config.width - 120  # Total width minus margins
        
        # For linked list, dictionary, or set, calculate size for single nodes
        if structure.type in ["linked_list", "dict", "set"]:
            element_size = min(
                (available_width - (num_elements - 1) * spacing) // num_elements,
                60  # Maximum size of 60px
            )
            total_width = num_elements * element_size + (num_elements - 1) * spacing
            
            # Add extra space for braces if it's a dictionary or set
            if structure.type in ["dict", "set"]:
                total_width += self.config.font_size * 2  # Space for left and right braces
        else:
            element_size = min(
                (available_width - (num_elements - 1) * spacing) // num_elements,
                60  # Maximum size of 60px
            )
            total_width = num_elements * element_size + (num_elements - 1) * spacing
        
        # Use position if provided, otherwise center horizontally
        if structure.position:
            start_x, y = structure.position
        else:
            start_x = (self.config.width - total_width) // 2
            y = base_y
            
        # Add extra left margin for dictionaries and sets
        if structure.type in ["dict", "set"]:
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
            
            # Add commas between elements for sets and dictionaries
            if (structure.type == "set" or structure.type == "dict") and i < num_elements - 1:
                comma_surface = self.font.render(", ", True, self.config.text_color)
                self.screen.blit(comma_surface, (rect.right + 5, y))
            
            if i in structure.labels:
                self.draw_labels(rect, structure.labels[i])
            if i in structure.pointers:
                self.draw_pointers(rect, structure.pointers[i])

        # Draw closing brace for dictionary and set with more spacing
        if structure.type in ["dict", "set"] and element_rects:
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
            # For other structures (array, dict, and set), keep center-to-center curved arrows
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
        
        # Process and draw video overlay
        video_surface = self.process_video_frame()
        if video_surface is not None:
            video_pos = (self.config.width - self.overlay_width - 20, 20)
            self.screen.blit(video_surface, video_pos)
        
        # Draw each structure
        base_y_offset = self.config.height // 4
        if frame.variables:
            base_y_offset += len(frame.variables) * (self.config.font_size + 5)
            
        for name, structure in frame.structures.items():
            self.draw_structure(structure, base_y_offset)
            base_y_offset += self.config.vertical_spacing
            
        # Draw frame text
        if frame.text:
            # Position text higher up (about 2/3 down the screen)
            text_y = int(self.config.height * 0.65)
            
            # Draw text first
            text_rect = pygame.Rect(
                60,
                text_y,
                self.config.width - 120,
                self.config.height//6
            )
            
            # Draw WAGMI gang text above the subtitles with smaller font
            title_font = pygame.font.Font(None, int(self.config.font_size * 1.2))
            title_text = "(WAGMI gang: 1/10000)"
            title_surface = title_font.render(title_text, True, self.config.text_color)
            title_rect = title_surface.get_rect(centerx=self.config.width//2, bottom=text_y - 10)
            self.screen.blit(title_surface, title_rect)
            
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