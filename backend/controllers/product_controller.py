import json
import os
from fastapi import HTTPException, UploadFile, File, Form
from typing import Optional
from services.product_service import ProductService
from infrastructure.database_repository import DatabaseRepository


class ProductController:
    """Контроллер для обработки запросов продуктов"""
    
    def __init__(self, product_service: ProductService, db_repository: DatabaseRepository):
        self.product_service = product_service
        self.db = db_repository
    
    async def upload_product(self, name: str, description: Optional[str], owner_id: int,
                           model_file: Optional[UploadFile], characteristics: Optional[str],
                           scenarios: Optional[str]) -> dict:
        """Загрузка продукта на платформу"""
        product_data = {
            'name': name,
            'description': description,
            'characteristics': json.loads(characteristics) if characteristics else [],
            'scenarios': json.loads(scenarios) if scenarios else []
        }
        
        model_file_content = None
        model_filename = None
        if model_file:
            model_file_content = await model_file.read()
            model_filename = model_file.filename
        
        result = self.product_service.upload_product(
            owner_id=owner_id,
            product_data=product_data,
            model_file=model_file_content,
            model_filename=model_filename
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    def get_products(self, owner_id: Optional[int] = None) -> list:
        """Получение списка всех доступных продуктов или продуктов владельца"""
        if owner_id:
            products = self.db.get_products_by_owner(owner_id)
            result = []
            for product in products:
                product_dict = dict(product)
                product_dict['scenarios'] = self.db.get_scenarios_by_product(product['id'])
                product_dict['characteristics'] = self.db.get_product_characteristics(product['id'])
                result.append(product_dict)
            return result
        else:
            products = self.product_service.get_all_available_products()
            return products
    
    def get_product(self, product_id: int) -> dict:
        """Получение детальной информации о продукте"""
        product = self.product_service.get_product_with_details(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        return product
    
    def get_product_scenarios(self, product_id: int) -> list:
        """Получение сценариев для продукта"""
        scenarios = self.db.get_scenarios_by_product(product_id)
        return scenarios
    
    def update_product(self, product_id: int, name: Optional[str], description: Optional[str],
                      owner_id: int) -> dict:
        """Обновление продукта"""
        product = self.db.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        if product['owner_id'] != owner_id:
            raise HTTPException(status_code=403, detail="Нет доступа к редактированию этого продукта")
        
        self.db.update_product(product_id, name=name, description=description)
        return {"success": True, "message": "Продукт обновлен"}
    
    def delete_product(self, product_id: int, owner_id: int) -> dict:
        """Удаление продукта"""
        product = self.db.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        if product['owner_id'] != owner_id:
            raise HTTPException(status_code=403, detail="Нет доступа к удалению этого продукта")
        
        self.db.delete_product(product_id)
        return {"success": True, "message": "Продукт удален"}
    
    def get_scenario_templates(self) -> list:
        """Получение шаблонов сценариев"""
        templates = self.product_service.get_scenario_templates()
        return templates

