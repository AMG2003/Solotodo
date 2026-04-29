from os import link

import oracledb
from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time
from extraccion import sub_datos

DB_USER = "system"
DB_PASSWORD = "system"
DB_DSN = "localhost:1521/XE" 

def conectar_db():
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        logging.info("Conexión a Oracle exitosa")
        return conn
    except Exception as e:
        logging.error(f"Error conectando a Oracle: {e}")
        raise

def configurar_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def scrape_data(driver):

    conn = conectar_db()  # Conexión a la base de datos
    
    driver.get('https://www.solotodo.com')

    try:
        wait = WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1udllag')))
        logging.info("Elemento encontrado")
        # 1. Definimos el XPath base de los 4 botones principales
        xpath_botones_principales = '//*[@id="__next"]/div/div[1]/header/div/div/div/div[2]/button'
    
        # Obtenemos la cantidad de botones (deberían ser 4: Tecnología, Hardware, etc.)
        botones = driver.find_elements(By.XPATH, xpath_botones_principales)
        cantidad_principales = len(botones)
        logging.info(f"Cantidad de botones principales encontrados: {cantidad_principales}")

        for i in range(1, 5):
            # Localizamos el botón principal por su índice (XPath empieza en 1)
            xpath_boton = f'({xpath_botones_principales})[{i}]'
            boton_principal = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_boton))
            )

            # 🔥 SCROLL (evita click interceptado)
            driver.execute_script("arguments[0].scrollIntoView(true);", boton_principal)
        
            nombre_seccion = boton_principal.text
            logging.info(f"Procesando sección: {nombre_seccion}")
        
            driver.execute_script("window.scrollTo(0, 0);")
            # 🔥 CLICK ROBUSTO
            driver.execute_script("arguments[0].click();", boton_principal)
            logging.info(f"Botón '{nombre_seccion}' clickeado")     
            time.sleep(1) # Breve pausa para que el menú se despliegue

            # Esperamos el contenedor del menú desplegado (ajusta clase si cambia)
            wait.until(
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

                try:
                    elemento = driver.find_element(By.XPATH, f"/html/body/div[2]/div[3]/div[2]/div[1]/div[{j}]")

                     # 🔍 Buscar si tiene <a>
                    link_elem = elemento.find_elements(By.TAG_NAME, "a")

                    if not link_elem:
                        logging.warning(f"Subcategoría {j} sin link → saltando")
                        continue

                    link = link_elem[0]

                    # validar href
                    href = link.get_attribute("href")
                    if not href:
                        logging.warning(f"Subcategoría sin href → saltando")
                        continue

                    nombre_subcategoria = link.text
                    logging.info(f"Subcategoría encontrada: {nombre_subcategoria}")

                    # 🔥 CLICK SEGURO
                    driver.execute_script("arguments[0].click();", link)

                except Exception as e:
                    logging.warning(f"No se pudo procesar subcategoría {j}: {e}")
                    continue

                # Esperamos que la página de productos cargue (ajusta el XPath si cambia)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div[4]/div[2]/div[1]')))

                sub_datos(driver, nombre_seccion, nombre_subcategoria,conn) # Función para extraer datos de la subcategoría

                # Volvemos al menú principal para la siguiente subcategoría
                boton_principal = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f'({xpath_botones_principales})[{i}]'))
                )
                #click para ingresar a la sigiuiente subcategoria
                boton_principal.click()

                logging.info(f"Reabriendo menú principal '{nombre_seccion}' para la siguiente subcategoría")

                # Esperamos que el menú se despliegue nuevamente
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]")))
                
        logging.info(f"Finalizada la sección {nombre_seccion}")

    except Exception as e:
        logging.error(f"Error al encontrar el elemento: {e}")