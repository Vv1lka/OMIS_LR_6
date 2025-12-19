"""
Контроллеры - обработка HTTP запросов
"""
from .auth_controller import AuthController
from .product_controller import ProductController
from .simulation_controller import SimulationController

__all__ = ['AuthController', 'ProductController', 'SimulationController']

