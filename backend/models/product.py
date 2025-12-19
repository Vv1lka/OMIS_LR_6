from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Product:
    """Класс продукта"""
    id: Optional[int]
    owner_id: int
    name: str
    description: Optional[str] = None
    model_file_path: Optional[str] = None
    model_file_url: Optional[str] = None
    status: str = 'pending'  # 'pending', 'verified', 'failed'
    created_at: Optional[str] = None
    scenarios: List[dict] = field(default_factory=list)
    characteristics: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        result = {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'description': self.description,
            'model_file_path': self.model_file_path,
            'model_file_url': self.model_file_url,
            'status': self.status,
            'created_at': self.created_at,
            'scenarios': self.scenarios,
            'characteristics': self.characteristics
        }
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            owner_id=data['owner_id'],
            name=data['name'],
            description=data.get('description'),
            model_file_path=data.get('model_file_path'),
            model_file_url=data.get('model_file_url'),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at'),
            scenarios=data.get('scenarios', []),
            characteristics=data.get('characteristics', [])
        )

