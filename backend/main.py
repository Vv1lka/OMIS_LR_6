from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pathlib import Path
import json as json_lib


from infrastructure.database_repository import DatabaseRepository
from infrastructure.file_storage import FileStorage


from services.auth_service import AuthService
from services.product_service import ProductService
from services.simulation_service import SimulationService


from controllers.auth_controller import AuthController
from controllers.product_controller import ProductController
from controllers.simulation_controller import SimulationController, CreateSessionRequest, InteractionRequest


db_repository = DatabaseRepository()
file_storage = FileStorage()


auth_service = AuthService(db_repository)
product_service = ProductService(db_repository, file_storage)
simulation_service = SimulationService(db_repository)


auth_controller = AuthController(auth_service)
product_controller = ProductController(product_service, db_repository)
simulation_controller = SimulationController(
    simulation_service, product_service, db_repository)


app = FastAPI(
    title="Платформа для виртуального тестирования и демонстрации продуктов")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent.parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

uploads_dir = Path(__file__).parent / "uploads" / "models"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads/models",
          StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.on_event("startup")
async def startup_event():
    db_repository.init_database()
    if not db_repository.get_user_by_username("test_owner"):
        auth_service.register_user(
            "test_owner", "owner@test.com", "password", "owner")
    if not db_repository.get_user_by_username("test_user"):
        auth_service.register_user(
            "test_user", "user@test.com", "password", "end_user")


# --- Аутентификация ---

@app.post("/api/auth/register")
async def register(username: str = Form(...), email: str = Form(...),
                   password: str = Form(...), user_type: str = Form(...)):
    """Регистрация пользователя"""
    return auth_controller.register(username, email, password, user_type)


@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Вход в систему"""
    return auth_controller.login(username, password)


# ---Управление продуктами ---

@app.post("/api/products/upload")
async def upload_product(
    name: str = Form(...),
    description: str = Form(None),
    owner_id: int = Form(...),
    model_file: UploadFile = File(None),
    characteristics: str = Form(None),
    scenarios: str = Form(None)
):
    """Загрузка продукта на платформу"""
    return await product_controller.upload_product(
        name, description, owner_id, model_file, characteristics, scenarios
    )


@app.get("/api/products")
async def get_products(owner_id: Optional[int] = None):
    """Получение списка всех доступных продуктов или продуктов владельца"""
    return product_controller.get_products(owner_id)


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Получение детальной информации о продукте"""
    return product_controller.get_product(product_id)


@app.get("/api/products/{product_id}/scenarios")
async def get_product_scenarios(product_id: int):
    """Получение сценариев для продукта"""
    return product_controller.get_product_scenarios(product_id)


@app.put("/api/products/{product_id}")
async def update_product_endpoint(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    owner_id: int = Form(...)
):
    """Обновление продукта"""
    return product_controller.update_product(product_id, name, description, owner_id)


@app.delete("/api/products/{product_id}")
async def delete_product_endpoint(product_id: int, owner_id: int):
    """Удаление продукта"""
    return product_controller.delete_product(product_id, owner_id)


# --- Симуляция ---

@app.post("/api/simulation/create-session")
async def create_simulation_session(request: CreateSessionRequest):
    """Создание сеанса тестирования"""
    import json as json_lib
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "main.py:create_simulation_session",
        "message": "Endpoint called with request data",
        "data": {
            "user_id": request.user_id,
            "product_id": request.product_id,
            "scenario_id": request.scenario_id
        },
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data, ensure_ascii=False) + '\n')
    except:
        pass
    result = simulation_controller.create_simulation_session(request)
    log_data2 = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "main.py:create_simulation_session",
        "message": "Session created successfully",
        "data": {"result": result},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data2, ensure_ascii=False) + '\n')
    except:
        pass
    return result


@app.post("/api/simulation/{session_id}/initialize")
async def initialize_simulation(session_id: int):
    """Инициализация виртуальной среды"""
    import json as json_lib
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "E",
        "location": "main.py:initialize_simulation",
        "message": "Initialize called",
        "data": {"session_id": session_id},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data, ensure_ascii=False) + '\n')
    except:
        pass
    # #endregion
    result = simulation_controller.initialize_simulation(session_id)
    # #region agent log
    log_data2 = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "E",
        "location": "main.py:initialize_simulation",
        "message": "Product loaded",
        "data": {"session_id": session_id},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data2, ensure_ascii=False) + '\n')
    except:
        pass
    # #endregion
    return result


@app.post("/api/simulation/{session_id}/interact")
async def process_interaction(session_id: int, request: InteractionRequest):
    """Обработка взаимодействия пользователя"""
    # #region agent log
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "C",
        "location": "main.py:process_interaction",
        "message": "Interaction endpoint called",
        "data": {
            "session_id": session_id,
            "interaction_type": request.interaction_type,
            "interaction_data": request.interaction_data
        },
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data, ensure_ascii=False) + '\n')
    except:
        pass
    result = simulation_controller.process_interaction(session_id, request)
    log_data2 = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "C",
        "location": "main.py:process_interaction",
        "message": "Interaction processed",
        "data": {"result": result},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open('/Users/Vilka/Documents/ВУЗ/ОМИС/лр6/.cursor/debug.log', 'a', encoding='utf-8') as f:
            f.write(json_lib.dumps(log_data2, ensure_ascii=False) + '\n')
    except:
        pass
    return result


@app.get("/api/simulation/{session_id}/state")
async def get_simulation_state(session_id: int):
    """Получение текущего состояния симуляции"""
    return simulation_controller.get_simulation_state(session_id)


@app.post("/api/simulation/{session_id}/finalize")
async def finalize_simulation(session_id: int):
    """Завершение сеанса симуляции"""
    return simulation_controller.finalize_simulation(session_id)


# --- Шаблоны сценариев ---
@app.get("/api/scenarios/templates")
async def get_scenario_templates():
    """Получение шаблонов сценариев"""
    return product_controller.get_scenario_templates()


# --- Главная страница ---
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    index_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding='utf-8')
    return "<h1>Платформа для виртуального тестирования и демонстрации продуктов</h1><p>Файл index.html не найден</p>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
