import logging
import time
from scraping import scrape_data , configurar_driver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analisis_precios.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
) 

def pipeline():
    driver = configurar_driver()   
    try:
        logging.info("Iniciando el proceso de scraping.")
        scrape_data(driver)
        logging.info("Scraping completado exitosamente.")
    except Exception as e:
        logging.error(f"Error durante el proceso de scraping: {e}")
    finally:
        time.sleep(2)  
        driver.quit()
        logging.info("Driver cerrado.")
   
if __name__ == "__main__":  
    pipeline()