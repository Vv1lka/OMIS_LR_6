import os
import json
from typing import Dict, Any, List, Optional
from infrastructure.database_repository import DatabaseRepository
from infrastructure.file_storage import FileStorage
from models.product import Product


class ProductService:
    """Сервис для работы с продуктами"""
    
    def __init__(self, db_repository: DatabaseRepository, file_storage: FileStorage):
        self.db = db_repository
        self.file_storage = file_storage
    
    def upload_product(self, owner_id: int, product_data: Dict[str, Any], 
                      model_file: bytes = None, model_filename: str = None) -> Dict[str, Any]:
        """
        Загрузка продукта на платформу
        Включает модель продукта, сценарии использования и характеристики
        """
        model_file_path = None
        if model_file and model_filename:
            model_file_path = self.file_storage.save_model_file(model_file, model_filename)
        
        product_id = self.db.create_product(
            owner_id=owner_id,
            name=product_data.get('name'),
            description=product_data.get('description'),
            model_file_path=model_file_path
        )
        
        characteristics = product_data.get('characteristics', [])
        for char in characteristics:
            self.db.add_product_characteristic(
                product_id=product_id,
                name=char.get('name'),
                value=char.get('value')
            )
        
        scenarios = product_data.get('scenarios', [])
        for scenario in scenarios:
            self.db.create_scenario(
                product_id=product_id,
                name=scenario.get('name'),
                description=scenario.get('description'),
                scenario_data=json.dumps(scenario.get('data', {}))
            )
        
        # Проверка совместимости (симуляция)
        compatibility_result = self.check_compatibility(product_id, model_file_path)
        
        if compatibility_result['success']:
            self.db.update_product_status(product_id, 'verified')
            return {
                'success': True,
                'product_id': product_id,
                'message': 'Продукт успешно загружен и проверен'
            }
        else:
            self.db.update_product_status(product_id, 'failed')
            return {
                'success': False,
                'product_id': product_id,
                'message': f"Ошибка проверки совместимости: {compatibility_result['error']}"
            }
    
    def check_compatibility(self, product_id: int, model_file_path: Optional[str]) -> Dict[str, Any]:
        """
        Проверка совместимости модели
        В реальной системе здесь была бы сложная логика проверки
        """

        if not model_file_path:
            return {'success': False, 'error': 'Файл модели не предоставлен'}
        

        if not os.path.exists(model_file_path):
            return {'success': False, 'error': 'Файл модели не найден'}
        

        file_size = os.path.getsize(model_file_path)
        if file_size == 0:
            return {'success': False, 'error': 'Файл модели пуст'}
        
        return {'success': True}
    
    def get_product_with_details(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Получение продукта со всеми деталями"""
        product = self.db.get_product(product_id)
        if not product:
            return None
        
        product_dict = dict(product)
        product_dict['scenarios'] = self.db.get_scenarios_by_product(product_id)
        product_dict['characteristics'] = self.db.get_product_characteristics(product_id)
        
        return product_dict
    
    def get_all_available_products(self) -> List[Dict[str, Any]]:
        """Получение всех доступных продуктов для пользователей"""
        products = self.db.get_all_products()
        result = []
        for product in products:
            product_dict = dict(product)
            product_dict['scenarios'] = self.db.get_scenarios_by_product(product['id'])
            result.append(product_dict)
        return result
    
    def get_scenario_templates(self) -> List[Dict[str, Any]]:
        """Получение всех шаблонов сценариев"""
        return self.db.get_scenario_templates()

