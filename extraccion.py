from selenium import webdriver
from selenium.webdriver.common.by import By     
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
import time
from db import insertar_productos

def configurar_driver():
    chrome_options = Options()
    return webdriver.Chrome(options=chrome_options)

def sub_datos(driver, nombre_seccion, nombre_subcategoria,conn):
    logging.info(f"Extrayendo datos de la sección '{nombre_seccion}' y subcategoría '{nombre_subcategoria}'")
    
    try:
        wait = WebDriverWait(driver,7)
        #identificamos la grilla de productos
        grilla=wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div[4]/div[2]/div[1]'))
        )
        if grilla:
           logging.info("Grilla de productos encontrada")
        else:
           logging.warning("Grilla de productos no encontrada")
        
        try:
            # Cambiar a mostrar 200 productos por página
            boton_svg = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[3]/div[3]/div/div/div[2]/div"))
            )
            boton_svg.click()

            #localizamos el menu desplegable de cantidad de productos
            wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/ul")))
            #localizamos la opcion de 200 productos por pagina
            opcion_200 = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/ul/li[6]"))
            )
            opcion_200.click()

            # Esperamos que la página se recargue con 200 productos (ajusta el XPath si cambia)
            wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[4]/div[2]/div[1]")))

        except Exception as e:
            logging.warning("no se pudo cambiar a 200")
        
        pagina = 1
        while True:
            logging.info(f"Scrapeando página {pagina}")

            # 🧲 Obtener productos
            productos = driver.find_elements(By.XPATH, "//div[contains(@class,'MuiGrid-root')]//a")

            productos_pagina = []

            for p in productos:
                try:
                    nombre_elem = p.find_elements(By.XPATH, ".//div[contains(@class,'MuiTypography-h5')]")
                    precio_elem = p.find_elements(By.XPATH, ".//div[contains(@class,'MuiTypography-h2')]")

                    if not nombre_elem or not precio_elem:
                        continue  # 🔥 evita errores

                    nombre = nombre_elem[0].text
                    precio = precio_elem[0].text
                    link = p.get_attribute("href")

                    
                    productos_pagina.append({
                        "seccion": nombre_seccion,
                        "subcategoria": nombre_subcategoria,
                        "nombre": nombre,
                        "precio": precio,
                        "link": link
                    })

                

                except Exception as e:
                    logging.warning(f"Error producto: {e}")  

            if productos_pagina:
             insertar_productos(productos_pagina,conn)            

            # 👉 Intentar ir a siguiente página
            try:
                boton_siguiente = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[3]/div[3]/div/div/div[3]/button[3]"))
                )

                if "disabled" in boton_siguiente.get_attribute("class"):
                    logging.info("Última página alcanzada")
                    break

                boton_siguiente.click()
                logging.info("Botón siguiente clickeado")
                pagina += 1
                time.sleep(3)

            except:
                logging.info("No hay botón siguiente → fin")
                break

    except Exception as e:
        logging.error(f"Error : {e}")