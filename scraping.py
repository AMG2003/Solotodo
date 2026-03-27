from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time
from extraccion import sub_datos

def configurar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def scrape_data(driver):
    
    driver.get('https://www.solotodo.com')

    try:
        wait = WebDriverWait(driver,10)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1udllag')))
        logging.info("Elemento encontrado")
        # 1. Definimos el XPath base de los 4 botones principales
        xpath_botones_principales = '//*[@id="__next"]/div/div[1]/header/div/div/div/div[2]/button'
    
        # Obtenemos la cantidad de botones (deberían ser 4: Tecnología, Hardware, etc.)
        botones = driver.find_elements(By.XPATH, xpath_botones_principales)
        cantidad_principales = len(botones)
        logging.info(f"Cantidad de botones principales encontrados: {cantidad_principales}")

        for i in range(1, cantidad_principales + 1):
            # Localizamos el botón principal por su índice (XPath empieza en 1)
            xpath_boton = f'({xpath_botones_principales})[{i}]'
            boton_principal = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_boton))
            )
        
            nombre_seccion = boton_principal.text
            logging.info(f"Procesando sección: {nombre_seccion}")
        
            # Hacemos clic para desplegar las categorías
            boton_principal.click()
            logging.info(f"Botón '{nombre_seccion}' clickeado")     
            time.sleep(1) # Breve pausa para que el menú se despliegue

            # Esperamos el contenedor del menú desplegado (ajusta clase si cambia)
            menu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]"))
            )

            # Obtener subcategorías
            subcategorias = driver.find_elements(
                By.XPATH,
                "/html/body/div[2]/div[3]/div[2]/div[1]/div/a"
            )

            cantidad_sub = len(subcategorias)
            logging.info(f"Cantidad de subcategorías encontradas: {cantidad_sub}")

            for j in range(1, cantidad_sub + 1):
                xpath_subcategoria = f"/html/body/div[2]/div[3]/div[2]/div[1]/div[{j}]/a/div/span"
                subcategoria = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_subcategoria))
                )
                nombre_subcategoria = subcategoria.text
                logging.info(f"Subcategoría encontrada: {nombre_subcategoria}")
                subcategoria.click()
                time.sleep(5) # Breve pausa para que la página se recargue
                sub_datos(driver, nombre_seccion, nombre_subcategoria) # Función para extraer datos de la subcategoría
                driver.back() # Volvemos a la página anterior para seleccionar la siguiente subcategoría
                logging.info(f"Volviendo al home")
                time.sleep(5) # Breve pausa para que la página se recargue
                 # 🔁 REABRIR menú SIEMPRE
                boton_principal = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f'({xpath_botones_principales})[{i}]'))
                )
                boton_principal.click()
                logging.info(f"Reabriendo menú principal '{nombre_seccion}' para la siguiente subcategoría")
                time.sleep(5) # Breve pausa para que el menú se despliegue nuevamente

        logging.info(f"Finalizada la sección {nombre_seccion}")

    except Exception as e:
        logging.error(f"Error al encontrar el elemento: {e}")