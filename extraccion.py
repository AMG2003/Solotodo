import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By     
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time

def configurar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def sub_datos(driver, nombre_seccion, nombre_subcategoria):
    logging.info(f"Extrayendo datos de la sección '{nombre_seccion}' y subcategoría '{nombre_subcategoria}'")
    # Aquí iría la lógica para extraer los datos específicos de cada subcategoría
    # Por ejemplo, podrías buscar los productos listados, sus precios, etc.
    # Este es un ejemplo genérico y debe ser adaptado a la estructura específica de la página
    try:
        grill = '//*[@id="__next"]/div/div[1]/main/div/div/div[4]/div[2]/div[1]'
        grill_wait= WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, grill))
        )
        logging.info("Grilla de productos encontrada")
        svg = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[3]/div[3]/div/div/div[2]/div"))
        )
        svg.click()
        time.sleep(5) # Esperamos a que se cargue la nueva sección después de hacer click
        li = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/ul/li[6]"))
        )
        li.click()
        time.sleep(5) # Esperamos a que se cargue la nueva sección después de hacer click

        try:
            numero_productos_string = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[4]/div[1]/div/div[1]/div/h5/text()[1]"))
            ).text
            numero_productos_int = int(numero_productos_string.split()[0])  # Extraemos el número de productos
            logging.info(f"Número de productos encontrados: {numero_productos_int}")
            
        except Exception as e:
            logging.error(f"Error al interactuar con la página: {e}")

        #productos = WebDriverWait(driver, 10).until(
            #EC.presence_of_all_elements_located((By.CLASS_NAME, 'nombre-clase-producto'))  # Cambia 'nombre-clase-producto' por la clase real
        #)
        #for producto in productos:
           # nombre_producto = producto.find_element(By.CLASS_NAME, 'nombre-clase').text  # Cambia 'nombre-clase' por la clase real
            #precio_producto = producto.find_element(By.CLASS_NAME, 'precio-clase').text  # Cambia 'precio-clase' por la clase real
            #logging.info(f"Producto: {nombre_producto}, Precio: {precio_producto}")
    except Exception as e:
        logging.error(f"Error al extraer datos de '{nombre_subcategoria}': {e}")