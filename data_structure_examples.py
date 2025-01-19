from frame import Frame, DataStructure
from typing import List, Dict, Any

def get_data_structure_examples(data_structures: List[str]) -> Dict[str, List[Frame]]:
    """Returns example frames for each specified data structure type
    
    Args:
        data_structures: List of data structure types to get examples for
        
    Returns:
        Dictionary mapping data structure type to list of example frames
    """
    examples = {}
    
    for ds_type in data_structures:
        if ds_type == 'array':
            examples[ds_type] = [
                Frame(
                    structures={
                        'main': DataStructure(
                            type="array",
                            elements=[-4, -1, -1, 0, 1, 2],
                            highlighted=[0],
                            labels={0: ["anchor"]},  # Label below cell
                            pointers={0: ["i"]}      # Pointer above cell with vertical arrow
                        )
                    },
                    variables={'res': [], 'i': 0},
                    text="Example of array with highlights, labels and pointers"
                ),
                Frame(
                    structures={
                        'main': DataStructure(
                            type="array",
                            elements=[-4, -1, -1, 0, 1, 2],
                            highlighted=[0, 1, 5],
                            arrows=[(1, 5)],  # Curved arrow showing relationship
                            pointers={0: ["i"], 1: ["L"], 5: ["R"]},  # Vertical arrows for pointers
                            labels={0: ["anchor"], 1: ["sum = -5"]}  # Labels below cells
                        )
                    },
                    variables={'res': [], 'i': 0, 'left': 1, 'right': 5},
                    text="Example of array with arrows between elements"
                )
            ]
        elif ds_type == 'linked_list':
            examples[ds_type] = [
                Frame(
                    structures={
                        'main': DataStructure(
                            type="linked_list",
                            elements=[1, 2, 3, 4, 5],
                            highlighted=[1, 2],
                            pointers={0: ["head"], 2: ["current"]},
                        )
                    },
                    variables={'current': 2},
                    text="Example of linked list with pointers and highlights"
                ),
                Frame(
                    structures={
                        'main': DataStructure(
                            type="linked_list",
                            elements=[1, 2, 3, 4, 5],
                            highlighted=[2],
                            arrows=[(0, 1), (1, 2)],  # Shows path taken
                            self_arrows=[2],  # Shows cycle
                            pointers={0: ["head"], 2: ["cycle"]},
                            is_doubly=False
                        )
                    },
                    variables={'current': 3},
                    text="Example of linked list with arrows and cycle"
                )
            ]
        elif ds_type == 'doubly_linked_list':
            examples[ds_type] = [
                Frame(
                    structures={
                        'main': DataStructure(
                            type="linked_list",
                            elements=[1, 2, 3, 4, 5],
                            is_doubly=True,
                            highlighted=[1, 2],
                            pointers={1: ["prev"], 2: ["current"], 3: ["next"]},
                        )
                    },
                    variables={'current': 2},
                    text="Example of doubly linked list with bidirectional pointers"
                ),
                Frame(
                    structures={
                        'main': DataStructure(
                            type="linked_list",
                            elements=[1, 2, 3, 4, 5],
                            is_doubly=True,
                            highlighted=[2],
                            self_arrows=[2],
                            pointers={2: ["cycle"]},
                        )
                    },
                    variables={'current': 3},
                    text="Example of doubly linked list with cycle"
                )
            ]
        elif ds_type == 'dict':
            examples[ds_type] = [
                Frame(
                    structures={
                        'main': DataStructure(
                            type="dict",
                            elements=[('nums[0]', -4), ('nums[1]', -1), ('nums[2]', -1), ('target', 5)],
                            highlighted=[0],  # Highlights the first key-value pair
                            pointers={0: ["current"]},
                            labels={0: ["checking"]}
                        )
                    },
                    variables={'i': 0},
                    text="Examining first element: nums[0] → -4"
                ),
                Frame(
                    structures={
                        'main': DataStructure(
                            type="dict",
                            elements=[('nums[0]', -4), ('nums[1]', -1), ('nums[2]', -1), ('target', 5)],
                            highlighted=[1, 2],  # Highlights two key-value pairs
                            arrows=[(1, 2)],  # Shows relationship between entries
                            labels={1: ["found duplicate"], 2: ["duplicate"]},
                            pointers={1: ["prev"], 2: ["current"]}
                        )
                    },
                    variables={'i': 1},
                    text="Found duplicate values: nums[1] and nums[2] both equal -1"
                )
            ]
        elif ds_type == 'set':
            examples[ds_type] = [
                Frame(
                    structures={
                        'main': DataStructure(
                            type="set",
                            elements=[1, 3, 5, 7],
                            highlighted=[0],  # Highlights first element
                            pointers={0: ["current"]},
                            labels={0: ["checking"]}
                        )
                    },
                    variables={'seen': {1}},
                    text="Examining first element in the set"
                ),
                Frame(
                    structures={
                        'main': DataStructure(
                            type="set",
                            elements=[1, 3, 5, 7],
                            highlighted=[1, 2],  # Highlights two elements
                            arrows=[(1, 2)],  # Shows relationship between elements
                            labels={1: ["found"], 2: ["target"]},
                            pointers={1: ["prev"], 2: ["current"]}
                        )
                    },
                    variables={'seen': {1, 3}},
                    text="Found target value in the set"
                )
            ]
        elif ds_type == 'tree':
            print("TREE IS CHOSEN")
            examples[ds_type] = [
                # Basic tree visualization
                Frame(
                    structures={
                        'main': DataStructure(
                            type="tree",
                            elements=[1, 2, 3, 4, 5, None, 7]
                        )
                    },
                    text="Starting with a binary tree",
                    variables={'current': 1}
                ),
                
                # Show highlighting and pointers
                Frame(
                    structures={
                        'main': DataStructure(
                            type="tree",
                            elements=[1, 2, 3, 4, 5, None, 7],
                            highlighted=[1, 4],  # Highlight current node and its child
                            pointers={1: ["current"], 4: ["left"]},
                            labels={1: ["parent"], 4: ["child"]}
                        )
                    },
                    text="Traversing the tree, examining node relationships",
                    variables={'visited': [1, 2, 4]}
                ),
                
                # Show relationships with arrows and multiple features
                Frame(
                    structures={
                        'main': DataStructure(
                            type="tree",
                            elements=[1, 2, 3, 4, 5, None, 7],
                            highlighted=[2, 3],  # Highlight sibling nodes
                            arrows=[(0, 2), (0, 3)],  # Show parent-child relationships
                            labels={2: ["left"], 3: ["right"]},
                            pointers={0: ["root"], 2: ["current"]}
                        )
                    },
                    text="Examining sibling relationships in the tree",
                    variables={'path': [1, 2]}
                )
            ]
        else:
            raise ValueError(f"Unsupported data structure type: {ds_type}")
            
    return examples 

def get_available_data_structures() -> List[str]:
    """Returns a list of all available data structure types that have examples
    
    Returns:
        List of supported data structure type strings
    """
    return ['array', 'linked_list', 'doubly_linked_list', 'dict', 'set', 'tree'] 