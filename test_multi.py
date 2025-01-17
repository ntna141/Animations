from simple_visualizer import SimpleVisualizer, VisualizerConfig
from frame import Frame, DataStructure

def test_multi_visualization():
    
    config = VisualizerConfig(width=1080, height=720)  
    visualizer = SimpleVisualizer(config)
    
    
    frames = [
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5]
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5]
                )
            },
            text="Starting with an array and a linked list"
        ),
        
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[1, 3],
                    labels={1: ["array[1]"], 3: ["array[3]"]}
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[1, 3],
                    labels={1: ["node.next"], 3: ["current"]}
                )
            },
            text="Highlighting elements in both structures"
        ),
        
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[1, 3],
                    pointers={1: ["L"], 3: ["R"]}
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[1, 3],
                    pointers={1: ["prev"], 3: ["curr"]}
                )
            },
            text="Adding pointers to both structures"
        ),
        
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5],
                    arrows=[(1, 3)],  
                    pointers={1: ["L"], 3: ["R"]}
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5],
                    arrows=[(0, 1), (1, 2), (2, 3), (3, 4)],  
                    highlighted=[2]
                )
            },
            text="Different arrow styles: curved for array, straight for list"
        ),
        
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5],
                    self_arrows=[2],
                    labels={2: ["pivot"]}
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5],
                    self_arrows=[4],
                    labels={4: ["tail"]}
                )
            },
            text="Self-pointing arrows in both structures"
        ),
        
        
        Frame(
            structures={
                'array': DataStructure(
                    type="array",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[0, 4],
                    arrows=[(0, 4)],
                    labels={0: ["start"], 4: ["end"]},
                    pointers={0: ["head"], 4: ["tail"]}
                ),
                'list': DataStructure(
                    type="linked_list",
                    elements=[1, 2, 3, 4, 5],
                    highlighted=[0, 2, 4],
                    arrows=[(0, 1), (1, 2), (2, 3), (3, 4)],
                    labels={0: ["head"], 2: ["middle"], 4: ["tail"]},
                    pointers={2: ["current"]}
                )
            },
            text="Showing multiple features at once"
        )
    ]
    
    
    visualizer.visualize_frames(frames, "test_multi.mp4")

if __name__ == "__main__":
    test_multi_visualization() 