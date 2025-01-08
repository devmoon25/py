from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging
import pandas as pd

# Configuración del archivo de log
logging.basicConfig(
    filename="consulta_runt.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def setup_driver():
    """Configura el driver de Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_vehicle_data(driver, placa, nit):
    """Extrae los datos de un vehículo usando Selenium."""
    try:
        # Navegar a la página principal
        driver.get("https://www.runt.gov.co/consultaCiudadana/#/consultaVehiculo")
        time.sleep(3)

        # Ingresar la placa
        placa_input = driver.find_element(By.XPATH, "//input[@id='noPlaca']")
        placa_input.clear()
        placa_input.send_keys(placa)

        # Seleccionar tipo de documento
        tipo_documento = Select(driver.find_element(By.XPATH, "//select[@id='tipoDocumento']"))
        tipo_documento.select_by_visible_text("NIT")  # Cambiar si el tipo de documento es diferente

        # Ingresar NIT
        nit_input = driver.find_element(By.XPATH, "//input[@id='noDocumento']")
        nit_input.clear()
        nit_input.send_keys(nit)

        # Capturar el captcha
        captcha_image = driver.find_element(By.XPATH, "//img[@id='imgCaptcha']")
        captcha_image.screenshot("captcha.png")

        # Resolver captcha manualmente
        captcha_solution = input(f"Captcha para la placa {placa}: ")

        # Ingresar captcha resuelto
        captcha_input = driver.find_element(By.XPATH, "//input[@id='captchatxt']")
        captcha_input.clear()
        captcha_input.send_keys(captcha_solution)

        # Hacer clic en el botón de consultar
        consultar_button = driver.find_element(By.XPATH, "//button[contains(text(),'Consultar Información')]")
        consultar_button.click()

        # Esperar los resultados (ajusta si es necesario)
        time.sleep(5)

        # Extraer los datos de la página
        data = {
            "placa": placa,
            "marca": driver.find_element(By.XPATH, "//div[text()='Marca']/following-sibling::div").text,
            "modelo": driver.find_element(By.XPATH, "//div[text()='Modelo']/following-sibling::div").text,
            "chasis": driver.find_element(By.XPATH, "//div[text()='Chasis']/following-sibling::div").text,
            # Agrega más campos según sea necesario
        }
        logging.info(f"Datos extraídos correctamente para la placa {placa}: {data}")
        return data

    except NoSuchElementException as e:
        logging.error(f"Elemento no encontrado para la placa {placa}: {e}")
    except TimeoutException as e:
        logging.error(f"Timeout al procesar la placa {placa}: {e}")
    except Exception as e:
        logging.error(f"Error inesperado para la placa {placa}: {e}")
    return None

def main():
    """Función principal para ejecutar el scraping."""
    # Leer las placas desde un archivo Excel
    placas_df = pd.read_excel("./data/placas.xlsx")
    resultados = []

    driver = setup_driver()
    for _, row in placas_df.iterrows():
        placa = row["placa"]
        nit = "890903938"  # Cambiar por el NIT requerido

        logging.info(f"Iniciando consulta para la placa: {placa}")
        data = extract_vehicle_data(driver, placa, nit)
        if data:
            resultados.append(data)

    driver.quit()

    # Guardar resultados en un archivo Excel
    resultados_df = pd.DataFrame(resultados)
    resultados_df.to_excel("./data/resultados_runt.xlsx", index=False)
    logging.info("Proceso completado. Resultados guardados en resultados_runt.xlsx")

if __name__ == "__main__":
    main()
