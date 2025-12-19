import json
import time
from typing import Dict, Any, Optional
from infrastructure.database_repository import DatabaseRepository


class SimulationEngine:
    """Движок симуляции для обработки взаимодействий с продуктами"""
    
    def __init__(self, session_id: int, db_repository: DatabaseRepository):
        self.session_id = session_id
        self.db = db_repository
        self.session = self.db.get_test_session(session_id)
        self.state = {}
        self.load_session_state()
    
    def load_session_state(self):
        """Загрузка состояния сеанса"""
        if self.session and self.session.get('session_data'):
            try:
                self.state = json.loads(self.session['session_data'])
            except:
                self.state = {}
        else:
            self.state = {
                'initialized': False,
                'interactions': [],
                'current_step': 0
            }
    
    def save_session_state(self):
        """Сохранение состояния сеанса"""
        session_data = json.dumps(self.state)
        self.db.update_test_session_data(self.session_id, session_data)
    
    def initialize_environment(self, product_data: Dict[str, Any], 
                               scenario_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Инициализация виртуальной среды для симуляции"""
        self.state['initialized'] = True
        self.state['product'] = {
            'id': product_data.get('id'),
            'name': product_data.get('name'),
            'model_file': product_data.get('model_file_path')
        }
        self.state['scenario'] = scenario_data or {}
        self.state['current_step'] = 0
        self.state['interactions'] = []
        
        self.save_session_state()
        
        return {
            'success': True,
            'environment': {
                'product': self.state['product'],
                'scenario': self.state['scenario'],
                'ready': True
            }
        }
    
    def process_interaction(self, interaction_type: str, 
                           interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка взаимодействия пользователя с продуктом"""
        if not self.state.get('initialized'):
            return {'success': False, 'error': 'Среда не инициализирована'}
        
        interaction_record = {
            'type': interaction_type,
            'data': interaction_data,
            'timestamp': time.time(),
            'step': self.state['current_step']
        }
        
        self.state['interactions'].append(interaction_record)
        self.state['current_step'] += 1
        
        self.db.add_interaction(
            session_id=self.session_id,
            interaction_type=interaction_type,
            interaction_data=json.dumps(interaction_data)
        )
        
        # Обрабатываем взаимодействие (симуляция)
        result = self._simulate_interaction(interaction_type, interaction_data)
        
        self.save_session_state()
        
        return {
            'success': True,
            'result': result,
            'step': self.state['current_step'],
            'state': self.state
        }
    
    def _simulate_interaction(self, interaction_type: str, 
                             interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Симуляция конкретного взаимодействия"""
        
        simulation_results = {
            'interaction_type': interaction_type,
            'processed': True,
            'response': f"Обработано взаимодействие типа: {interaction_type}",
            'updated_state': {}
        }
        
        if interaction_type == 'click':
            simulation_results['response'] = 'Клик обработан'
            simulation_results['updated_state'] = {'clicked': True}
        elif interaction_type == 'rotate':
            simulation_results['response'] = 'Поворот обработан'
            simulation_results['updated_state'] = {'rotation': interaction_data.get('angle', 0)}
        elif interaction_type == 'zoom':
            simulation_results['response'] = 'Масштабирование обработано'
            simulation_results['updated_state'] = {'zoom': interaction_data.get('level', 1.0)}
        else:
            simulation_results['response'] = f'Взаимодействие {interaction_type} обработано'
        
        return simulation_results
    
    def get_current_state(self) -> Dict[str, Any]:
        """Получение текущего состояния симуляции"""
        return {
            'initialized': self.state.get('initialized', False),
            'product': self.state.get('product'),
            'scenario': self.state.get('scenario'),
            'current_step': self.state.get('current_step', 0),
            'interactions_count': len(self.state.get('interactions', []))
        }
    
    def finalize_session(self):
        """Завершение сеанса симуляции"""
        self.db.update_test_session_status(self.session_id, 'completed')
        return {
            'success': True,
            'session_id': self.session_id,
            'total_interactions': len(self.state.get('interactions', [])),
            'final_state': self.state
        }


class SimulationService:
    """Сервис для работы с симуляцией"""
    
    def __init__(self, db_repository: DatabaseRepository):
        self.db = db_repository
    
    def create_simulation_session(self, user_id: int, product_id: int, 
                                 scenario_id: int = None) -> Dict[str, Any]:
        """Создание нового сеанса симуляции"""
        session_id = self.db.create_test_session(
            user_id=user_id,
            product_id=product_id,
            scenario_id=scenario_id
        )
        
        return {
            'success': True,
            'session_id': session_id
        }
    
    def get_simulation_engine(self, session_id: int) -> SimulationEngine:
        """Получение движка симуляции для сеанса"""
        return SimulationEngine(session_id, self.db)

