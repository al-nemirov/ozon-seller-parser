"""
Stage 2 — Парсинг деталей товаров.
====================================
Открывает каждую ссылку из product_links.txt и извлекает данные товара.
"""

import csv
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from .config import ParserConfig
from .browser import create_driver

logger = logging.getLogger(__name__)

# Колонки CSV
FIELDNAMES = [
    "Название",
    "Ссылка на товар",
    "Изображение",
    "Артикул",
    "Автор",
    "Серия",
    "Год выпуска",
    "Описание",
]


def extract_text(soup: BeautifulSoup, selectors: list, default: str = "Нет данных") -> str:
    """Извлечь текст по списку CSS-селекторов (первый найденный)."""
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.text.strip()
    return default


def extract_description(soup: BeautifulSoup) -> str:
    """Извлечь полное описание из JSON-LD разметки."""
    try:
        script_tag = soup.find("script", text=re.compile(r"@context"))
        if script_tag:
            json_data = json.loads(script_tag.string.strip())
            if "description" in json_data:
                return json_data["description"].strip()
    except Exception as e:
        logger.debug(f"Не удалось извлечь описание из JSON-LD: {e}")
    return "Нет описания"


def extract_article(link: str) -> str:
    """Извлечь артикул (ID товара) из URL."""
    match = re.search(r"/product/.+-(\d+)/?", link)
    return match.group(1) if match else "Нет артикула"


def extract_attribute(soup: BeautifulSoup, href_pattern: str) -> str:
    """Извлечь атрибут товара по паттерну ссылки (автор, серия и т.д.)."""
    try:
        el = soup.select_one(f'div[data-widget="webShortCharacteristics"] a[href*="/{href_pattern}/"]')
        return el.text.strip() if el else "Нет данных"
    except Exception:
        return "Нет данных"


def parse_product(soup: BeautifulSoup, link: str) -> dict:
    """
    Извлечь все данные товара со страницы.

    Args:
        soup: распаршенный HTML.
        link: URL товара.

    Returns:
        Словарь с данными товара.
    """
    name = extract_text(soup, ["h1", 'div[data-widget="webProductHeading"] h1'])

    image = soup.select_one('div[data-widget="webGallery"] img')
    image_url = image.get("src") if image else "Нет изображения"

    return {
        "Название": name,
        "Ссылка на товар": link,
        "Изображение": image_url,
        "Артикул": extract_article(link),
        "Автор": extract_attribute(soup, "person"),
        "Серия": extract_attribute(soup, "series"),
        "Год выпуска": "Нет данных",  # Требует отдельной логики
        "Описание": extract_description(soup),
    }


def run_scraper(config: ParserConfig) -> None:
    """
    Запуск Stage 2: парсинг деталей товаров.

    Args:
        config: настройки парсера.
    """
    logger.info("=" * 60)
    logger.info("  Stage 2: Парсинг деталей товаров")
    logger.info("=" * 60)

    links_path = Path(config.links_file)
    if not links_path.exists():
        logger.error(f"Файл не найден: {config.links_file}")
        logger.error("Сначала запустите Stage 1: python run.py collect")
        return

    with open(links_path, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        logger.warning("Файл ссылок пуст")
        return

    logger.info(f"Ссылок для обработки: {len(links)}")

    driver = create_driver(config.chrome_path or None)
    driver.implicitly_wait(config.implicit_wait)

    success = 0
    errors = 0

    try:
        with open(config.output_file, mode="w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES, delimiter=";")
            writer.writeheader()

            for i, link in enumerate(links, 1):
                try:
                    driver.get(link)
                    time.sleep(config.page_pause)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    row = parse_product(soup, link)
                    writer.writerow(row)

                    success += 1
                    if i % 10 == 0 or i == len(links):
                        logger.info(f"[{i}/{len(links)}] Обработано: {success} | Ошибок: {errors}")

                except Exception as e:
                    errors += 1
                    logger.warning(f"[{i}/{len(links)}] Ошибка: {link} — {e}")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        try:
            driver.quit()
            logger.info("Браузер закрыт")
        except Exception:
            pass

    logger.info("=" * 60)
    logger.info(f"Готово! Успешно: {success} | Ошибок: {errors}")
    logger.info(f"Результат: {config.output_file}")
    logger.info("=" * 60)
