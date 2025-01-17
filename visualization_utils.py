from typing import Dict, Any, Tuple
import pygame
import cv2
import os
import glob

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

class VisualizationConfig:
    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height
        self.background_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.element_color = (100, 100, 100)
        self.highlight_color = (255, 200, 200)
        self.arrow_color = (0, 100, 200)
        self.pointer_color = (50, 50, 200)
        self.label_color = (100, 100, 100)
        self.font_size = height // 35
        self.element_size = width // 8
        self.element_spacing = width // 24
        self.vertical_spacing = height // 8 