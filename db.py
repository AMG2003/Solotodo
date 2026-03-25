import oracledb
import logging 

# 🔐 Configuración (ajusta con tus datos)
DB_USER = "system"
DB_PASSWORD = "system"
DB_DSN = "localhost:1521/XE"  # ejemplo típico Oracle XE


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
        
def insertar_productos(productos):
    conn = conectar_db()
    cursor = conn.cursor()

    data = [
        (
            p["seccion"],
            p["subcategoria"],
            p["nombre"],
            float(p["precio"].replace("$", "").replace(".", "").replace(",", "")),
            p["link"]
        )
        for p in productos
    ]

    try:
        cursor.executemany("""
            INSERT INTO PRODUCTOS (seccion, subcategoria, nombre, precio, link)
            VALUES (:1, :2, :3, :4, :5)
        """, data)

        conn.commit()
        logging.info(f"{len(productos)} insertados")

    except Exception as e:
        logging.warning(f"Error insertando (posible duplicado): {e}")

    finally:
        cursor.close()
        conn.close()    