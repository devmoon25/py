import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_logging(log_file="consulta_runt.log"):
    """Configura el sistema de logs."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def resolve_captcha(driver):
    """Resolver el captcha usando una solución placeholder o integración con API."""
    try:
        captcha_img = driver.find_element(By.ID, "imgCaptcha")
        captcha_img.screenshot("captcha.png")
        # Aquí se integraría una API para resolver el captcha.
        captcha_solution = "placeholder_solution"
        return captcha_solution
    except NoSuchElementException as e:
        logging.error("No se encontró el elemento del captcha: %s", e)
        return None

def extract_element_text(driver, xpath):
    """Intenta extraer texto de un elemento de la página usando su XPath."""
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except NoSuchElementException:
        logging.warning(f"Elemento no encontrado: {xpath}")
        return None

def select_dropdown_option(driver, xpath, visible_text):
    """Selecciona una opción en un menú desplegable."""
    try:
        select_element = Select(driver.find_element(By.XPATH, xpath))
        select_element.select_by_visible_text(visible_text)
        logging.info(f"Opción seleccionada en el dropdown: {visible_text}")
    except NoSuchElementException as e:
        logging.error("No se pudo encontrar el elemento del dropdown: %s", e)
    except Exception as e:
        logging.error("Error al seleccionar la opción del dropdown: %s", e)

def wait_for_page_load(timeout=5):
    """Espera un tiempo predeterminado para que la página cargue."""
    logging.info(f"Esperando {timeout} segundos para que cargue la página.")
    time.sleep(timeout)
