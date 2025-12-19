from pathlib import Path
from typing import Optional


class FileStorage:
    """Класс для работы с файловым хранилищем"""
    
    def __init__(self):
        self.upload_dir = Path(__file__).parent.parent / "uploads"
        self.models_dir = self.upload_dir / "models"
        self.scenarios_dir = self.upload_dir / "scenarios"
        
        self.upload_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.scenarios_dir.mkdir(exist_ok=True)
    
    def save_model_file(self, file_content: bytes, filename: str) -> str:
        file_path = self.models_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return str(file_path)
    
    def get_model_file_path(self, filename: str) -> Optional[Path]:
        file_path = self.models_dir / filename
        if file_path.exists():
            return file_path
        return None
    
    def delete_model_file(self, file_path: str) -> bool:
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

