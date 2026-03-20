"""
Конфигурация парсера.
=====================
Все настройки вынесены в один файл для удобства.
Скопируйте config.example.json -> config.json и заполните свои данные.
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT_DIR / "config.json"
DEFAULT_CONFIG_FILE = ROOT_DIR / "config.example.json"


@dataclass
class ParserConfig:
    """Настройки парсера."""

    # URL страницы продавца на OZON
    seller_url: str = ""

    # Путь к браузеру (пустая строка = системный Chrome)
    chrome_path: str = ""

    # Файл со ссылками на товары
    links_file: str = "product_links.txt"

    # Файл с результатами парсинга
    output_file: str = "product_details.csv"

    # Лог-файл
    log_file: str = "parser.log"

    # Пауза между скроллами (секунды)
    scroll_pause: int = 5

    # Пауза между загрузкой страниц товаров (секунды)
    page_pause: int = 7

    # Максимум попыток без новых товаров перед остановкой
    max_retries: int = 50

    # Таймаут ожидания элементов (секунды)
    implicit_wait: int = 15

    # Таймаут скроллинга (секунды)
    scroll_timeout: int = 1200

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "ParserConfig":
        """Загрузить конфигурацию из JSON-файла."""
        config_path = path or CONFIG_FILE

        if not config_path.exists():
            print(f"Конфигурация не найдена: {config_path}")
            print(f"Скопируйте config.example.json -> config.json и заполните данные.")
            sys.exit(1)

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def validate(self) -> None:
        """Проверить обязательные поля."""
        if not self.seller_url or "YOUR-SELLER" in self.seller_url:
            print("Ошибка: укажите seller_url в config.json")
            print("Пример: https://www.ozon.ru/seller/my-shop-123456/books-16500/")
            sys.exit(1)
