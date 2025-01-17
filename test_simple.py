from simple_visualizer import SimpleVisualizer, VisualizerConfig
from frame import Frame, DataStructure

def test_array_visualization():
    
    config = VisualizerConfig(width=1080, height=1920)  
    visualizer = SimpleVisualizer(config)
    
    frames = [
        Frame(
            structures={'main': DataStructure(
                type="array",
                elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            )},
            variables={'res': [], 'left': 0, 'right': 4},
            text="Starting with array [1, 2, 3, 4, 5] and initializing variables Current sum = nums[left] + nums[right] = 1 + 5 = 6 Current sum = nums[left] + nums[right] = 1 + 5 = 6"
        ),
        
        Frame(
            structures={'main': DataStructure(
                type="array",
                elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
,
                highlighted=[0, 4],
                pointers={0: ["L"], 4: ["R"]}
            )},
            variables={'res': [], 'left': 0, 'right': 4, 'sum': 6},
            text="Current sum = nums[left] + nums[right] = 1 + 5 = 6"
        ),
        
        Frame(
            structures={'main': DataStructure(
                type="array",
                elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                highlighted=[0, 3],
                pointers={0: ["L"], 3: ["R"]}
            )},
            variables={'res': [], 'left': 0, 'right': 3, 'sum': 5},
            text="Moving right pointer left, new sum = 1 + 4 = 5"
        ),
        
        Frame(
            structures={'main': DataStructure(
                type="array",
                elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                highlighted=[1, 3],
                pointers={1: ["L"], 3: ["R"]}
            )},
            variables={'res': [[1, 4]], 'left': 1, 'right': 3, 'sum': 6},
            text="Found a pair! Added [1, 4] to result. Moving left pointer right."
        )
    ]
    
    visualizer.visualize_frames(frames, "test_animation.mp4")

if __name__ == "__main__":
    test_array_visualization() 