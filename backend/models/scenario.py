from typing import Optional
from dataclasses import dataclass


@dataclass
class Scenario:
    """Класс сценария использования"""
    id: Optional[int]
    product_id: int
    name: str
    description: Optional[str] = None
    scenario_data: Optional[str] = None
    is_template: bool = False
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'description': self.description,
            'scenario_data': self.scenario_data,
            'is_template': self.is_template,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Scenario':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            product_id=data['product_id'],
            name=data['name'],
            description=data.get('description'),
            scenario_data=data.get('scenario_data'),
            is_template=bool(data.get('is_template', False)),
            created_at=data.get('created_at')
        )

