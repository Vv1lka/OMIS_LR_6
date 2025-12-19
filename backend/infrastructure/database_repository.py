import sqlite3
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')

if not os.path.exists(DATABASE_PATH):
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'database.db')


class DatabaseRepository:
    """Репозиторий для работы с базой данных"""
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Контекстный менеджер для работы с БД"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    @staticmethod
    def init_database():
        """Инициализация базы данных - создание таблиц"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT NOT NULL CHECK(user_type IN ('owner', 'end_user')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    model_file_path TEXT,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'verified', 'failed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    scenario_data TEXT,
                    is_template BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_characteristics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    characteristic_name TEXT NOT NULL,
                    characteristic_value TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    scenario_id INTEGER,
                    session_data TEXT,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    interaction_type TEXT NOT NULL,
                    interaction_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions(id)
                )
            """)
            
            conn.commit()
    

    @staticmethod
    def create_user(username: str, email: str, password_hash: str, user_type: str) -> int:
        """Создание нового пользователя"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, user_type)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, user_type))
            return cursor.lastrowid
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по имени"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create_product(owner_id: int, name: str, description: str = None, 
                       model_file_path: str = None) -> int:
        """Создание нового продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (owner_id, name, description, model_file_path, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (owner_id, name, description, model_file_path))
            return cursor.lastrowid
    
    @staticmethod
    def update_product_status(product_id: int, status: str):
        """Обновление статуса продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products SET status = ? WHERE id = ?
            """, (status, product_id))
    
    @staticmethod
    def get_product(product_id: int) -> Optional[Dict[str, Any]]:
        """Получение продукта по ID"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_all_products() -> List[Dict[str, Any]]:
        """Получение всех продуктов"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE status = 'verified'")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_products_by_owner(owner_id: int) -> List[Dict[str, Any]]:
        """Получение всех продуктов владельца"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE owner_id = ?", (owner_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_product(product_id: int, name: str = None, description: str = None, 
                       model_file_path: str = None):
        """Обновление продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if model_file_path is not None:
                updates.append("model_file_path = ?")
                params.append(model_file_path)
            
            if updates:
                params.append(product_id)
                cursor.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", params)
    
    @staticmethod
    def delete_product(product_id: int):
        """Удаление продукта и связанных данных"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product_characteristics WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM scenarios WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    

    @staticmethod
    def create_scenario(product_id: int, name: str, description: str = None,
                       scenario_data: str = None, is_template: bool = False) -> int:
        """Создание сценария использования"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scenarios (product_id, name, description, scenario_data, is_template)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, name, description, scenario_data, 1 if is_template else 0))
            return cursor.lastrowid
    
    @staticmethod
    def get_scenarios_by_product(product_id: int) -> List[Dict[str, Any]]:
        """Получение сценариев для продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scenarios WHERE product_id = ?", (product_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_scenario_templates() -> List[Dict[str, Any]]:
        """Получение всех шаблонов сценариев"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scenarios WHERE is_template = 1")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def add_product_characteristic(product_id: int, name: str, value: str):
        """Добавление характеристики продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO product_characteristics (product_id, characteristic_name, characteristic_value)
                VALUES (?, ?, ?)
            """, (product_id, name, value))
    
    @staticmethod
    def get_product_characteristics(product_id: int) -> List[Dict[str, Any]]:
        """Получение характеристик продукта"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM product_characteristics WHERE product_id = ?
            """, (product_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create_test_session(user_id: int, product_id: int, scenario_id: int = None,
                           session_data: str = None) -> int:
        """Создание сеанса тестирования"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_sessions (user_id, product_id, scenario_id, session_data, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (user_id, product_id, scenario_id, session_data))
            return cursor.lastrowid
    
    @staticmethod
    def get_test_session(session_id: int) -> Optional[Dict[str, Any]]:
        """Получение сеанса тестирования"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def update_test_session_status(session_id: int, status: str):
        """Обновление статуса сеанса"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            if status == 'completed':
                cursor.execute("""
                    UPDATE test_sessions 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (status, session_id))
            else:
                cursor.execute("""
                    UPDATE test_sessions SET status = ? WHERE id = ?
                """, (status, session_id))
    
    @staticmethod
    def update_test_session_data(session_id: int, session_data: str):
        """Обновление данных сеанса"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_sessions SET session_data = ? WHERE id = ?
            """, (session_data, session_id))
    
    @staticmethod
    def add_interaction(session_id: int, interaction_type: str, interaction_data: str):
        """Добавление взаимодействия"""
        with DatabaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interactions (session_id, interaction_type, interaction_data)
                VALUES (?, ?, ?)
            """, (session_id, interaction_type, interaction_data))

