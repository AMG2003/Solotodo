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
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def sub_datos(driver, nombre_seccion, nombre_subcategoria):
    logging.info(f"Extrayendo datos de la sección '{nombre_seccion}' y subcategoría '{nombre_subcategoria}'")
    

    try:
        grilla=WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[1]/main/div/div/div[4]/div[2]/div[1]'))
        )
        if grilla:
           logging.info("Grilla de productos encontrada")
        else:
           logging.warning("Grilla de productos no encontrada")
        
        try:
            boton_svg = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/main/div/div/div[3]/div[3]/div/div/div[2]/div"))
            )
            boton_svg.click()
            time.sleep(5) # Esperamos a que se cargue la nueva sección después de hacer click
            opcion_200 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/ul/li[6]"))
            )
            opcion_200.click()
            time.sleep(3) # Esperamos a que se cargue la nueva sección después de hacer click

        except Exception as e:
            logging.warning("no se pudo cambiar a 200")
        
        pagina = 1
        while True:
            logging.info(f"Scrapeando página {pagina}")

            # 🧲 Obtener productos
            productos = driver.find_elements(By.XPATH, "//div[contains(@class,'MuiGrid-root')]//a")

            for p in productos:
                try:
                    nombre_elem = p.find_elements(By.XPATH, ".//div[contains(@class,'MuiTypography-h5')]")
                    precio_elem = p.find_elements(By.XPATH, ".//div[contains(@class,'MuiTypography-h2')]")

                    if not nombre_elem or not precio_elem:
                        continue  # 🔥 evita errores

                    nombre = nombre_elem[0].text
                    precio = precio_elem[0].text
                    link = p.get_attribute("href")

                    # 🔥 EXTRAER ESPECIFICACIONES
                    specs = {}

                    try:
                        filas = driver.find_elements(By.XPATH, "//table//tr")

                        for fila in filas:
                            try:
                                clave = fila.find_element(By.XPATH, ".//th").text.strip()
                                valor = fila.find_element(By.XPATH, ".//td").text.strip()
                                specs[clave] = valor
                            except:
                                continue

                    except Exception as e:
                        logging.warning(f"No specs: {e}")

                    # 🔥 guardar en BD
                    insertar_productos({
                        "seccion": nombre_seccion,
                        "subcategoria": nombre_subcategoria,
                        "nombre": nombre,
                        "precio": precio,
                        "link": link,
                        "specs": specs
                    })

                    time.sleep(1)  # evita bloqueo

                except Exception as e:
                    logging.warning(f"Error producto: {e}")      

            # 👉 Intentar ir a siguiente página
            try:
                boton_siguiente = WebDriverWait(driver, 5).until(
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