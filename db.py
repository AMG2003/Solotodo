import oracledb
import logging 
# 🔐 Configuración (ajusta con tus datos)
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
        
def insertar_productos(productos,conn):
    cursor = conn.cursor()

    try:
        for p in productos:

            # 1. INSERTAR CATEGORIA
            cursor.executemany("""
                MERGE INTO dim_categoria c
                USING (SELECT :1 nombre FROM dual) src
                ON (c.nombre = src.nombre)
                WHEN NOT MATCHED THEN
                    INSERT (nombre) VALUES (src.nombre)
            """, [p["seccion"]])

            # 2. OBTENER ID CATEGORIA
            cursor.execute("SELECT id_categoria FROM dim_categoria WHERE nombre = :1", [p["seccion"]])
            id_categoria = cursor.fetchone()[0]

            # 3. INSERTAR SUBCATEGORIA
            cursor.executemany("""
                MERGE INTO dim_subcategoria s
                USING (SELECT :1 nombre, :2 id_categoria FROM dual) src
                ON (s.nombre = src.nombre AND s.id_categoria = src.id_categoria)
                WHEN NOT MATCHED THEN
                    INSERT (nombre, id_categoria) VALUES (src.nombre, src.id_categoria)
            """, [p["subcategoria"], id_categoria])

            # 4. OBTENER ID SUBCATEGORIA
            cursor.execute("""
                SELECT id_subcategoria 
                FROM dim_subcategoria 
                WHERE nombre = :1 AND id_categoria = :2
            """, [p["subcategoria"], id_categoria])

            id_subcategoria = cursor.fetchone()[0]

            # 5. INSERTAR PRODUCTO
            cursor.executemany("""
                MERGE INTO dim_producto dp
                USING (SELECT :link AS link FROM dual) src
                ON (dp.link = src.link)
                WHEN NOT MATCHED THEN
                    INSERT (nombre, link, id_subcategoria)
                    VALUES (:nombre, :link, :id_subcategoria)
            """, {
                "link": p["link"],
                "nombre": p["nombre"],
                "id_subcategoria": id_subcategoria
            })

            # 6. OBTENER ID PRODUCTO
            cursor.execute("SELECT id_producto FROM dim_producto WHERE link = :1", [p["link"]])
            id_producto = cursor.fetchone()[0]

            # 7. INSERTAR PRECIO (HISTÓRICO)
            precio_num = float(p["precio"].replace("$", "").replace(".", "").replace(",", ""))

            cursor.executemany("""
                INSERT INTO fact_precios (id_producto, precio)
                VALUES (:1, :2)
            """, [id_producto, precio_num])

        conn.commit()
        logging.info(f"{len(productos)} productos insertados correctamente")

    except Exception as e:
        logging.error(f"Error insertando: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()