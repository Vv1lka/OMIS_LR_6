import json
import os
from fastapi import HTTPException
from typing import Optional
from pydantic import BaseModel
from services.simulation_service import SimulationService
from services.product_service import ProductService
from infrastructure.database_repository import DatabaseRepository


class CreateSessionRequest(BaseModel):
    user_id: int
    product_id: int
    scenario_id: Optional[int] = None


class InteractionRequest(BaseModel):
    interaction_type: str
    interaction_data: dict


class SimulationController:
    """Контроллер для обработки запросов симуляции"""
    
    def __init__(self, simulation_service: SimulationService, 
                 product_service: ProductService, db_repository: DatabaseRepository):
        self.simulation_service = simulation_service
        self.product_service = product_service
        self.db = db_repository
    
    def create_simulation_session(self, request: CreateSessionRequest) -> dict:
        """Создание сеанса тестирования"""
        result = self.simulation_service.create_simulation_session(
            user_id=request.user_id,
            product_id=request.product_id,
            scenario_id=request.scenario_id
        )
        return result
    
    def initialize_simulation(self, session_id: int) -> dict:
        """Инициализация виртуальной среды"""
        session = self.db.get_test_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Сеанс не найден")
        
        product = self.product_service.get_product_with_details(session['product_id'])
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        model_file_path = product.get('model_file_path')
        if model_file_path:
            filename = os.path.basename(model_file_path)
            product['model_file_url'] = f"/uploads/models/{filename}"
        
        scenario_data = None
        if session.get('scenario_id'):
            scenarios = self.db.get_scenarios_by_product(session['product_id'])
            scenario = next((s for s in scenarios if s['id'] == session['scenario_id']), None)
            if scenario and scenario.get('scenario_data'):
                scenario_data = json.loads(scenario['scenario_data'])
        
        engine = self.simulation_service.get_simulation_engine(session_id)
        result = engine.initialize_environment(product, scenario_data)
        return result
    
    def process_interaction(self, session_id: int, request: InteractionRequest) -> dict:
        """Обработка взаимодействия пользователя"""
        engine = self.simulation_service.get_simulation_engine(session_id)
        result = engine.process_interaction(request.interaction_type, request.interaction_data)
        return result
    
    def get_simulation_state(self, session_id: int) -> dict:
        """Получение текущего состояния симуляции"""
        engine = self.simulation_service.get_simulation_engine(session_id)
        return engine.get_current_state()
    
    def finalize_simulation(self, session_id: int) -> dict:
        """Завершение сеанса симуляции"""
        engine = self.simulation_service.get_simulation_engine(session_id)
        result = engine.finalize_session()
        return result

