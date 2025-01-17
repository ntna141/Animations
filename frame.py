from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any, Union

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
        structure = DataStructure(
            type="linked_list",
            elements=elements,
            highlighted=kwargs.pop('highlighted', None),
            arrows=kwargs.pop('arrows', None),
            self_arrows=kwargs.pop('self_arrows', None),
            labels=kwargs.pop('labels', None),
            pointers=kwargs.pop('pointers', None)
        )
        return cls(structures={'main': structure}, **kwargs) 