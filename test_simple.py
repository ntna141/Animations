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

def test_set_visualization():
    config = VisualizerConfig(width=1080, height=1920)
    visualizer = SimpleVisualizer(config)
    
    frames = [
        # Basic set visualization
        Frame(
            structures={
                'main': DataStructure(
                    type="set",
                    elements=[1, 3, 5, 7, 9]
                )
            },
            text="Starting with a set of odd numbers",
            variables={'target': 5}
        ),
        
        # Highlighting elements with pointers
        Frame(
            structures={
                'main': DataStructure(
                    type="set",
                    elements=[1, 3, 5, 7, 9],
                    highlighted=[0, 1],
                    pointers={0: ["prev"], 1: ["current"]}
                )
            },
            text="Searching through the set",
            variables={'seen': {1, 3}, 'target': 5}
        ),
        
        # Showing relationships with arrows
        Frame(
            structures={
                'main': DataStructure(
                    type="set",
                    elements=[1, 3, 5, 7, 9],
                    highlighted=[2],
                    arrows=[(1, 2)],  # Arrow from previous to current
                    labels={2: ["found target!"]},
                    pointers={2: ["current"]}
                )
            },
            text="Found target value 5 in the set",
            variables={'seen': {1, 3, 5}, 'target': 5}
        ),
        
        # Multiple features combined
        Frame(
            structures={
                'main': DataStructure(
                    type="set",
                    elements=[1, 3, 5, 7, 9],
                    highlighted=[2, 4],
                    arrows=[(2, 4)],  # Show relationship between elements
                    labels={2: ["sum = 14"], 4: ["complement"]},
                    pointers={2: ["a"], 4: ["b"]}
                )
            },
            text="Found pair (5, 9) with sum = 14",
            variables={'sum': 14, 'pairs': [(5, 9)]}
        )
    ]
    
    visualizer.visualize_frames(frames, "test_set.mp4")

def test_dict_visualization():
    config = VisualizerConfig(width=1080, height=1920)
    visualizer = SimpleVisualizer(config)
    
    frames = [
        # Basic dictionary visualization
        Frame(
            structures={
                'main': DataStructure(
                    type="dict",
                    elements=[('a', 1), ('b', 3), ('c', 5), ('d', 7)],
                )
            },
            text="Starting with a dictionary mapping letters to numbers",
            variables={'target': 'c'}
        ),
        
        # Highlighting elements with pointers
        Frame(
            structures={
                'main': DataStructure(
                    type="dict",
                    elements=[('a', 1), ('b', 3), ('c', 5), ('d', 7)],
                    highlighted=[0, 1],
                    pointers={0: ["prev"], 1: ["current"]}
                )
            },
            text="Searching through the dictionary",
            variables={'current_key': 'b'}
        ),
        
        # Showing relationships with arrows
        Frame(
            structures={
                'main': DataStructure(
                    type="dict",
                    elements=[('a', 1), ('b', 3), ('c', 5), ('d', 7)],
                    highlighted=[2],
                    arrows=[(1, 2)],  # Arrow from previous to current
                    labels={2: ["found key!"]},
                    pointers={2: ["current"]}
                )
            },
            text="Found target key 'c' in the dictionary",
            variables={'current_key': 'c', 'value': 5}
        ),
        
        # Multiple features combined
        Frame(
            structures={
                'main': DataStructure(
                    type="dict",
                    elements=[('a', 1), ('b', 3), ('c', 5), ('d', 7)],
                    highlighted=[1, 3],
                    arrows=[(1, 3)],  # Show relationship between entries
                    labels={1: ["sum = 10"], 3: ["complement"]},
                    pointers={1: ["x"], 3: ["y"]}
                )
            },
            text="Found pair (b:3, d:7) with sum = 10",
            variables={'sum': 10, 'pairs': [('b', 'd')]}
        )
    ]
    
    visualizer.visualize_frames(frames, "test_dict.mp4")

def test_tree_visualization():
    config = VisualizerConfig(width=1080, height=1920)
    visualizer = SimpleVisualizer(config)
    
    # Complete binary tree test
    frames = [
        # Basic tree visualization
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                )
            },
            text="Starting with a complete binary tree with 4 levels",
            variables={'root': 1}
        ),
        
        # Highlighting nodes with pointers
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    highlighted=[1, 2],  # Highlight nodes at level 1
                    pointers={0: ["root"], 2: ["current"]}
                )
            },
            text="Traversing level 1 of the tree",
            variables={'current': 3}
        ),
        
        # Showing path with arrows
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    highlighted=[2],
                    arrows=[(0, 1), (1, 2)],  # Show path taken
                    labels={2: ["target found"]},
                    pointers={0: ["root"], 2: ["current"]}
                )
            },
            text="Found target node with value 3",
            variables={'current': 3}
        ),
    ]
    
    visualizer.visualize_frames(frames, "test_complete_tree.mp4")
    
    # Unbalanced tree test
    unbalanced_frames = [
        # Basic unbalanced tree
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, None, 6, None, 8, 9, None, None, None, None, None, None, 16]
                )
            },
            text="Starting with an unbalanced binary tree",
            variables={'root': 1}
        ),
        
        # Highlighting deep path
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, None, 6, None, 8, 9, None, None, None, None, None, None, 16],
                    highlighted=[0, 1, 3, 7, 15],  # Highlight path to deepest node
                    arrows=[(0, 1), (1, 3), (3, 7), (7, 15)],  # Show path
                    labels={15: ["deepest node"]},
                    pointers={0: ["root"], 15: ["current"]}
                )
            },
            text="Found deepest node at level 4",
            variables={'depth': 4}
        ),
        
        # Show left-heavy subtree
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, None, 6, None, 8, 9, None, None, None, None, None, None, 16],
                    highlighted=[1, 3, 7, 8],  # Highlight left-heavy part
                    arrows=[(1, 3), (3, 7), (3, 8)],  # Show connections
                    labels={1: ["height=4"], 3: ["height=3"]},
                    pointers={1: ["unbalanced"]}
                )
            },
            text="Left subtree is deeper than right subtree",
            variables={'left_height': 4, 'right_height': 1}
        ),
        
        # Multiple features combined
        Frame(
            structures={
                'main': DataStructure(
                    type="tree",
                    elements=[1, 2, 3, 4, None, 6, None, 8, 9, None, None, None, None, None, None, 16],
                    highlighted=[3, 7, 8],
                    arrows=[(7, 8)],  # Show sibling relationship
                    labels={3: ["parent"], 7: ["left"], 8: ["right"]},
                    pointers={3: ["p"], 7: ["l"], 8: ["r"]}
                )
            },
            text="Examining siblings in the unbalanced subtree",
            variables={'parent': 4}
        )
    ]
    
    visualizer.visualize_frames(unbalanced_frames, "test_unbalanced_tree.mp4")

if __name__ == "__main__":
    # test_linked_list_visualization()
    # test_doubly_linked_list_visualization()
    # test_set_visualization()
    # test_dict_visualization()
    test_tree_visualization() 