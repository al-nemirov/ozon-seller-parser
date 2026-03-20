"""
Управление браузером.
=====================
Инициализация undetected-chromedriver с обходом антибот-защиты.
"""

import logging
from typing import Optional

import undetected_chromedriver as uc

logger = logging.getLogger(__name__)


def create_driver(chrome_path: Optional[str] = None) -> uc.Chrome:
    """
    Создать экземпляр браузера с обходом антибот-защиты.

    Args:
        chrome_path: путь к исполняемому файлу Chrome (None = системный).

    Returns:
        Настроенный экземпляр Chrome WebDriver.
    """
    options = uc.ChromeOptions()

    if chrome_path:
        options.binary_location = chrome_path

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    logger.info("Запуск браузера...")
    driver = uc.Chrome(options=options)

    return driver
