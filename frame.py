from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any, Union
from data_structures import Node, TreeNode

@dataclass
class DataStructure:
    """Represents a single data structure in a frame"""
    type: str  
    elements: List[Any]  
    position: Optional[Tuple[int, int]] = None  
    highlighted: List[int] = None  
    arrows: List[Tuple[int, int]] = None  
    self_arrows: List[int] = None  
    labels: Dict[int, List[str]] = None  
    pointers: Dict[int, List[str]] = None  
    is_doubly: bool = False  # Add is_doubly property
    
    def __post_init__(self):
        if self.highlighted is None:
            self.highlighted = []
        if self.arrows is None:
            self.arrows = []
        if self.self_arrows is None:
            self.self_arrows = []
        if self.labels is None:
            self.labels = {}
        if self.pointers is None:
            self.pointers = {}

@dataclass
class Frame:
    """Represents a single frame in the animation"""
    structures: Dict[str, DataStructure]  
    variables: Dict[str, Any] = None  # Track algorithm variables like res=[], queue=[], etc.
    duration: str = "3s"  
    line: Optional[int] = None  
    text: Optional[str] = None  
    pre_duration: str = "1s"  
    post_duration: str = "2s"  
    
    def __post_init__(self):
        if self.structures is None:
            self.structures = {}
        if self.variables is None:
            self.variables = {}
            
    @classmethod
    def from_array(cls, elements: List[Any], **kwargs) -> 'Frame':
        """Create a frame from a single array for backward compatibility"""
        structure = DataStructure(
            type="array",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None)
        )
        return cls(structures={'main': structure}, **kwargs)
    
    @classmethod
    def from_linked_list(cls, elements: List[Any], **kwargs) -> 'Frame':
        """Create a frame from a single linked list"""
        # Convert array input into linked list nodes
        if elements and not isinstance(elements[0], Node):
            nodes = []
            for value in elements:
                nodes.append(Node(value))
            # Link the nodes
            for i in range(len(nodes) - 1):
                nodes[i].next = nodes[i + 1]
            elements = nodes
            
        structure = DataStructure(
            type="linked_list",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None),
            is_doubly=kwargs.pop('is_doubly', False)  # Handle is_doubly property
        )
        return cls(structures={'main': structure}, **kwargs) 
    
    @classmethod
    def from_dict(cls, dictionary: Dict[Any, Any], **kwargs) -> 'Frame':
        """Create a frame from a dictionary
        
        Args:
            dictionary: The dictionary to visualize
            **kwargs: Additional frame parameters
            
        Returns:
            Frame object configured to display the dictionary
        """
        # Convert dictionary into list of tuples
        elements = list(dictionary.items())
        
        structure = DataStructure(
            type="dict",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None)
        )
        return cls(structures={'main': structure}, **kwargs)
        
    @classmethod
    def from_set(cls, set_elements: set, **kwargs) -> 'Frame':
        """Create a frame from a set
        
        Args:
            set_elements: The set to visualize
            **kwargs: Additional frame parameters
            
        Returns:
            Frame object configured to display the set
        """
        # Convert set into sorted list for consistent visualization
        elements = sorted(list(set_elements))
        
        structure = DataStructure(
            type="set",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None)
        )
        return cls(structures={'main': structure}, **kwargs)
        
    @classmethod
    def from_tree(cls, elements: List[Any], **kwargs) -> 'Frame':
        """Create a frame from a binary tree
        
        Args:
            elements: List of values to create tree from, or a TreeNode root
            **kwargs: Additional frame parameters
            
        Returns:
            Frame object configured to display the binary tree
        """
        # Convert array input into tree nodes
        if elements and not isinstance(elements[0], TreeNode):
            nodes = []
            for i, value in enumerate(elements):
                if value is not None:
                    nodes.append(TreeNode(value))
                else:
                    nodes.append(None)
                    
            # Link the nodes (using level order / array representation)
            for i in range(len(nodes)):
                if nodes[i] is not None:
                    left_idx = 2 * i + 1
                    right_idx = 2 * i + 2
                    if left_idx < len(nodes):
                        nodes[i].left = nodes[left_idx]
                    if right_idx < len(nodes):
                        nodes[i].right = nodes[right_idx]
            elements = nodes[0] if nodes else None
            
        structure = DataStructure(
            type="tree",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None)
        )
        return cls(structures={'main': structure}, **kwargs) 