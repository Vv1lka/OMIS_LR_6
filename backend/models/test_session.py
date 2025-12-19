from typing import Optional
from dataclasses import dataclass


@dataclass
class TestSession:
    """Класс сеанса тестирования"""
    id: Optional[int]
    user_id: int
    product_id: int
    scenario_id: Optional[int] = None
    session_data: Optional[str] = None
    status: str = 'active'  # 'active', 'completed'
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'scenario_id': self.scenario_id,
            'session_data': self.session_data,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TestSession':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            product_id=data['product_id'],
            scenario_id=data.get('scenario_id'),
            session_data=data.get('session_data'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            completed_at=data.get('completed_at')
        )

