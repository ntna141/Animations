from simple_visualizer import SimpleVisualizer, VisualizerConfig
from frame import Frame

def test_array_visualization():
    
    config = VisualizerConfig(width=1080, height=720)  
    visualizer = SimpleVisualizer(config)
    
    
    frames = [
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            text="Starting with array [1, 2, 3, 4, 5]"
        ),
        
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            highlighted=[1, 3],
            text="Highlighting elements at indices 1 and 3",
            labels={1: ["second"], 3: ["fourth"]}
        ),
        
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            highlighted=[1, 3],
            pointers={1: ["L"], 3: ["R"]},
            text="Adding pointers L and R"
        ),
        
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            highlighted=[1, 3],
            pointers={1: ["L"], 3: ["R"]},
            arrows=[(1, 3)],
            text="Drawing arrow from L to R"
        ),
        
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            highlighted=[2],
            self_arrows=[2],
            text="Element points to itself"
        ),
        
        
        Frame(
            elements=[1, 2, 3, 4, 5],
            highlighted=[0, 4],
            arrows=[(0, 4)],
            labels={0: ["start"], 4: ["end"]},
            pointers={0: ["head"], 4: ["tail"]},
            text="Showing multiple features at once"
        )
    ]
    
    
    visualizer.visualize_frames(frames, "test_animation.mp4")

if __name__ == "__main__":
    test_array_visualization() 