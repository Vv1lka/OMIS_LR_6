import hashlib
from typing import Optional, Dict, Any
from infrastructure.database_repository import DatabaseRepository
from models.user import User


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, db_repository: DatabaseRepository):
        self.db = db_repository
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Проверка пароля"""
        return AuthService.hash_password(password) == password_hash
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентификация пользователя"""
        user_data = self.db.get_user_by_username(username)
        if not user_data:
            return None
        
        if self.verify_password(password, user_data['password_hash']):
            # Удаляем пароль из результата
            user_dict = dict(user_data)
            user_dict.pop('password_hash', None)
            return user_dict
        
        return None
    
    def register_user(self, username: str, email: str, password: str, user_type: str) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        # Проверяем существование пользователя
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return {'success': False, 'error': 'Пользователь с таким именем уже существует'}
        
        password_hash = self.hash_password(password)
        user_id = self.db.create_user(username, email, password_hash, user_type)
        
        return {
            'success': True,
            'user_id': user_id,
            'username': username
        }

