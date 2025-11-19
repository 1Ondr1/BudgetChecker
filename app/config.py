from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "app/templates")
BASE_CATEGORIES = ["Еда", "Транспорт", "Коммунальные услуги", "Развлечения", "Покупки", "Здоровье", "Образование"]
