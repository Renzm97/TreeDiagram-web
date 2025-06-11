from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

class RelationType(str, Enum):
    AND = "and"
    OR = "or"

class TreeNode(BaseModel):
    name: str
    children: Optional[List['TreeNode']] = None
    relation_type: Optional[RelationType] = None
    
    class Config:
        json_encoders = {
            RelationType: lambda v: v.value
        }

# 允许前向引用
TreeNode.model_rebuild()

class TreeDiagramRequest(BaseModel):
    root_node: TreeNode
    
class TreeDiagramResponse(BaseModel):
    success: bool
    message: str
    image_path: Optional[str] = None 