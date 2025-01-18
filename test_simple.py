from simple_visualizer import SimpleVisualizer, VisualizerConfig
from frame import Frame, DataStructure
from data_structures import Node

def test_linked_list_visualization():
    config = VisualizerConfig(width=1080, height=1920)
    visualizer = SimpleVisualizer(config)
    
    frames = [
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            text="Starting with a singly linked list: 1 -> 2 -> 3 -> 4 -> 5",
            variables={'current': 1}
        ),
        
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            highlighted=[1, 2],
            pointers={0: ["head"], 2: ["current"]},
            text="Traversing the linked list",
            variables={'current': 2}
        ),
        
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            highlighted=[2],
            arrows=[(0, 1), (1, 2)],
            self_arrows=[2],
            pointers={0: ["head"], 2: ["cycle"]},
            text="Found a cycle at node 3",
            variables={'current': 3}
        )
    ]
    
    visualizer.visualize_frames(frames, "test_linked_list.mp4")

def test_doubly_linked_list_visualization():
    config = VisualizerConfig(width=1080, height=1920)
    visualizer = SimpleVisualizer(config)
    
    frames = [
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            is_doubly=True,
            arrows=[(0, 1)],
            text="Starting with a doubly linked list",
            variables={'current': 1}
        ),
        
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            is_doubly=True,
            highlighted=[1, 2],
            pointers={1: ["prev"], 2: ["current"], 3: ["next"]},
            text="Moving forward in the doubly linked list",
            variables={'current': 2}
        ),
        
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            is_doubly=True,
            highlighted=[2, 1],
            pointers={1: ["current"], 2: ["next"]},
            text="Moving backward in the doubly linked list",
            variables={'current': 1}
        ),
        
        Frame.from_linked_list(
            elements=[1, 2, 3, 4, 5],
            is_doubly=True,
            highlighted=[2],
            self_arrows=[2],
            pointers={2: ["cycle"]},
            text="Cycle detection in doubly linked list",
            variables={'current': 3}
        )
    ]
    
    visualizer.visualize_frames(frames, "test_doubly_linked_list.mp4")

if __name__ == "__main__":
    test_linked_list_visualization()
    # test_doubly_linked_list_visualization() 