from fastapi import HTTPException, Form
from services.auth_service import AuthService
from infrastructure.database_repository import DatabaseRepository


class AuthController:
    """Контроллер для обработки запросов аутентификации"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def register(self, username: str, email: str, password: str, user_type: str) -> dict:
        """Регистрация пользователя"""
        if user_type not in ['owner', 'end_user']:
            raise HTTPException(status_code=400, detail="Неверный тип пользователя")
        
        result = self.auth_service.register_user(username, email, password, user_type)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return result
    
    def login(self, username: str, password: str) -> dict:
        """Вход в систему"""
        user = self.auth_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
        
        return user

