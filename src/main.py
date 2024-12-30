import logging
import time
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

# Configuración del archivo de log
logging.basicConfig(
    filename="consulta_runt.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_runt_model():
    """ Carga el modelo preentrenado para resolver captchas del RUNT, registrando clases personalizadas.
    """
    from tensorflow.keras.layers import LSTM  # Importar la clase LSTM directamente

    class CTCLayer(layers.Layer):
        def __init__(self, name=None):
            super().__init__(name=name)
            self.loss_fn = tf.keras.backend.ctc_batch_cost

    model_path = "./models/runt.h5"
    model = load_model(
        model_path,
        custom_objects={"CTCLayer": CTCLayer, "LSTM": LSTM}
    )
    return model

def preprocess_captcha(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (204, 53))
    img = np.expand_dims(img, axis=-1)
    img = img / 255.0
    return np.expand_dims(img, axis=0)

def resolve_captcha_with_model(model, image_path):
    processed_image = preprocess_captcha(image_path)
    prediction = model.predict(processed_image)
    return decode_predictions(prediction)

def decode_predictions(pred):
    characters = ['2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'c', 'd', 'e', 'f', 
                  'g', 'h', 'k', 'm', 'n', 'p', 'r', 'w', 'x', 'y']
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    results = tf.keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :5]
    decoded_text = [
        ''.join([characters[c] for c in res if c != -1]) for res in results.numpy()
    ]
    return decoded_text[0]

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_full_vehicle_data(driver, placa, nit, runt_model):
    data = {}
    try:
        driver.get("https://www.runt.com.co/consultaCiudadana/#/consultaVehiculo")
        time.sleep(5)

        # Ingresar placa
        driver.find_element(By.ID, "noPlaca").send_keys(placa)

        # Seleccionar tipo de documento
        Select(driver.find_element(By.XPATH, "//select[@formcontrolname='tipoDocumento']")).select_by_visible_text("NIT")

        # Ingresar NIT
        driver.find_element(By.XPATH, "//input[@formcontrolname='numeroDocumento']").send_keys(nit)

        # Capturar y resolver captcha
        captcha_img = driver.find_element(By.ID, "imgCaptcha")
        captcha_img.screenshot("captcha.png")
        captcha_solution = resolve_captcha_with_model(runt_model, "captcha.png")
        driver.find_element(By.XPATH, "//input[@formcontrolname='captcha']").send_keys(captcha_solution)
        driver.find_element(By.XPATH, "//button[contains(text(),'Consultar')]").click()

        time.sleep(5)

        # Extraer datos generales
        data["placa"] = placa
        data["tipo_combustible"] = driver.find_element(By.XPATH, "//div[text()='Tipo Combustible']/following-sibling::div").text
        data["marca"] = driver.find_element(By.XPATH, "//div[text()='Marca']/following-sibling::div").text
        data["modelo"] = driver.find_element(By.XPATH, "//div[text()='Modelo']/following-sibling::div").text
        data["chasis"] = driver.find_element(By.XPATH, "//div[text()='Chasis']/following-sibling::div").text
        data["cilindraje"] = driver.find_element(By.XPATH, "//div[text()='Cilindraje']/following-sibling::div").text
        data["linea"] = driver.find_element(By.XPATH, "//div[text()='Línea']/following-sibling::div").text
        data["color"] = driver.find_element(By.XPATH, "//div[text()='Color']/following-sibling::div").text
        data["motor"] = driver.find_element(By.XPATH, "//div[text()='Motor']/following-sibling::div").text
        data["vin"] = driver.find_element(By.XPATH, "//div[text()='VIN']/following-sibling::div").text
        data["fecha_matricula"] = driver.find_element(By.XPATH, "//div[text()='Fecha Matrícula']/following-sibling::div").text
        data["autoridad"] = driver.find_element(By.XPATH, "//div[text()='Autoridad']/following-sibling::div").text
        data["soat"] = driver.find_element(By.XPATH, "//div[text()='SOAT']/following-sibling::div").text
        data["tecnomecanica"] = driver.find_element(By.XPATH, "//div[text()='Tecnomecánica']/following-sibling::div").text
        data["blindado"] = driver.find_element(By.XPATH, "//div[text()='Blindado']/following-sibling::div").text
        data["nivel_blindaje"] = driver.find_element(By.XPATH, "//div[text()='Nivel Blindaje']/following-sibling::div").text
        data["fecha_blindaje"] = driver.find_element(By.XPATH, "//div[text()='Fecha Blindaje']/following-sibling::div").text
        data["fecha_desblindaje"] = driver.find_element(By.XPATH, "//div[text()='Fecha Desblindaje']/following-sibling::div").text
        data["numero_resolucion"] = driver.find_element(By.XPATH, "//div[text()='Número Resolución']/following-sibling::div").text
        data["fecha_expedicion"] = driver.find_element(By.XPATH, "//div[text()='Fecha Expedición']/following-sibling::div").text
        data["tipo_autorizacion"] = driver.find_element(By.XPATH, "//div[text()='Tipo Autorización']/following-sibling::div").text
        data["nro_licencia"] = driver.find_element(By.XPATH, "//div[text()='Nro Licencia']/following-sibling::div").text
        data["tipo_servicio"] = driver.find_element(By.XPATH, "//div[text()='Tipo Servicio']/following-sibling::div").text
        data["estado_vehiculo"] = driver.find_element(By.XPATH, "//div[text()='Estado Vehículo']/following-sibling::div").text
        data["clase_vehiculo"] = driver.find_element(By.XPATH, "//div[text()='Clase Vehículo']/following-sibling::div").text
        data["numero_serie"] = driver.find_element(By.XPATH, "//div[text()='Número Serie']/following-sibling::div").text
        data["tipo_carroceria"] = driver.find_element(By.XPATH, "//div[text()='Tipo Carrocería']/following-sibling::div").text
        data["regrabacion_motor"] = driver.find_element(By.XPATH, "//div[text()='Regrabación Motor']/following-sibling::div").text
        data["nro_regrabacion_motor"] = driver.find_element(By.XPATH, "//div[text()='Nro Regrabación Motor']/following-sibling::div").text
        data["regrabacion_chasis"] = driver.find_element(By.XPATH, "//div[text()='Regrabación Chasis']/following-sibling::div").text
        data["nro_regrabacion_chasis"] = driver.find_element(By.XPATH, "//div[text()='Nro Regrabación Chasis']/following-sibling::div").text
        data["regrabacion_serie"] = driver.find_element(By.XPATH, "//div[text()='Regrabación Serie']/following-sibling::div").text
        data["nro_regrabacion_serie"] = driver.find_element(By.XPATH, "//div[text()='Nro Regrabación Serie']/following-sibling::div").text
        data["regrabacion_vin"] = driver.find_element(By.XPATH, "//div[text()='Regrabación VIN']/following-sibling::div").text
        data["nro_regrabacion_vin"] = driver.find_element(By.XPATH, "//div[text()='Nro Regrabación VIN']/following-sibling::div").text
        data["capacidad_carga"] = driver.find_element(By.XPATH, "//div[text()='Capacidad Carga']/following-sibling::div").text
        data["capacidad_pasajeros_sentados"] = driver.find_element(By.XPATH, "//div[text()='Capacidad Pasajeros Sentados']/following-sibling::div").text
        data["capacidad_pasajeros"] = driver.find_element(By.XPATH, "//div[text()='Capacidad Pasajeros']/following-sibling::div").text
        data["solicitudes"] = driver.find_element(By.XPATH, "//div[text()='Solicitudes']/following-sibling::div").text

    except NoSuchElementException as e:
        logging.error(f"Elemento no encontrado para la placa {placa}: {str(e)}")
    except Exception as e:
        logging.error(f"Error al procesar la placa {placa}: {str(e)}")
    finally:
        return data


def main():
    placas_df = pd.read_excel("./data/placas.xlsx")
    resultados = []

    runt_model = load_runt_model()
    logging.info("Modelo RUNT cargado correctamente.")

    driver = setup_driver()

    for _, row in placas_df.iterrows():
        placa = row["placa"]
        nit = "890903938"  # NIT fijo, puede hacerse configurable

        logging.info(f"Iniciando consulta para la placa: {placa}")
        data = extract_full_vehicle_data(driver, placa, nit, runt_model)

        if data:
            resultados.append(data)
            logging.info(f"Consulta exitosa para la placa: {placa}")
        else:
            logging.error(f"Consulta fallida para la placa: {placa}")

    driver.quit()

    # Guardar resultados en Excel
    resultados_df = pd.DataFrame(resultados)
    resultados_df.to_excel("./data/runt_resultados.xlsx", index=False)

if __name__ == "__main__":
    main()
