from typing import Optional
from dataclasses import dataclass


@dataclass
class Interaction:
    """Класс взаимодействия пользователя с продуктом"""
    id: Optional[int]
    session_id: int
    interaction_type: str
    interaction_data: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'interaction_type': self.interaction_type,
            'interaction_data': self.interaction_data,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Interaction':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            session_id=data['session_id'],
            interaction_type=data['interaction_type'],
            interaction_data=data.get('interaction_data'),
            timestamp=data.get('timestamp')
        )

