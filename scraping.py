import pandas as pd 
from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time
import os

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

        for i in range(1, cantidad_principales + 1):
            # Localizamos el botón principal por su índice (XPath empieza en 1)
            xpath_boton = f'({xpath_botones_principales})[{i}]'
            boton_principal = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_boton))
            )
        
            nombre_seccion = boton_principal.text
            print(f"--- Entrando a la sección: {nombre_seccion} ---")
        
            # Hacemos clic para desplegar las categorías
            boton_principal.click()
            time.sleep(1) # Breve pausa para que el menú se despliegue

            # 2. Buscamos los enlaces (categorías) dentro del menú desplegado
            # El XPath de las categorías suele estar en un contenedor que aparece al clickear
             # Ajusta este XPath según lo que veas en el inspector al abrir el menú
            xpath_categorias = "//div[contains(@class,'css')]//a[contains(@href, '/')]" 
            categorias_internas = driver.find_elements(By.XPATH, xpath_categorias)
        
            urls_categorias = [c.get_attribute("href") for c in categorias_internas]

            logging.info(f"Encontradas {len(urls_categorias)} categorías en la sección {nombre_seccion}")

            for url in urls_categorias:
                print(f"Scrapeando categoría: {url}")
                driver.get(url)
            
                # --- AQUÍ VA TU LÓGICA PARA EXTRAER LOS PRODUCTOS ---
                # extraer_datos_de_la_pagina(driver)
            
                # Volvemos atrás o a la página principal para seguir con el siguiente
                driver.back() 
                time.sleep(1)
            
                # IMPORTANTE: Si al volver atrás el menú se cierra, 
                # tendrás que volver a clickear el botón principal 'i'
                driver.find_element(By.XPATH, xpath_boton).click()
                time.sleep(1)

            print(f"Finalizada la sección {nombre_seccion}")
    except Exception as e:
        logging.error(f"Error al encontrar el elemento: {e}")