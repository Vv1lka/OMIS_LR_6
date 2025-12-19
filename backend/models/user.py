from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """Класс пользователя системы"""
    id: Optional[int]
    username: str
    email: str
    password_hash: Optional[str] = None
    user_type: str = 'end_user'  # 'owner' или 'end_user'
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'created_at': self.created_at
        }
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash'),
            user_type=data.get('user_type', 'end_user'),
            created_at=data.get('created_at')
        )

