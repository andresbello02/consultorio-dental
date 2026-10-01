import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="consultorio_dental",
        port=3306
    )


def insertar_usuario(nombre, correo, password, rol="paciente"):

    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        # -----------------------------------
        # 1. Verificar si el correo ya existe
        # -----------------------------------

        cursor.execute(
            "SELECT id FROM usuarios WHERE correo = %s",
            (correo,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:
            print("❌ El correo ya está registrado.")
            return False

        # -----------------------------------
        # 2. Crear contraseña segura
        # -----------------------------------

        password_hash = generate_password_hash(password)

        # -----------------------------------
        # 3. Insertar usuario
        # -----------------------------------

        sql = """
            INSERT INTO usuarios
            (nombre, correo, password, rol)
            VALUES (%s, %s, %s, %s)
        """

        valores = (
            nombre,
            correo,
            password_hash,
            rol
        )

        cursor.execute(sql, valores)
        conexion.commit()

        print("===================================")
        print("✅ USUARIO REGISTRADO CORRECTAMENTE")
        print("Nombre:", nombre)
        print("Correo:", correo)
        print("Rol:", rol)
        print("===================================")

        return True

    except mysql.connector.Error as e:

        print("===================================")
        print("❌ ERROR DE MYSQL")
        print("Código:", e.errno)
        print("Mensaje:", e.msg)
        print("===================================")

        return False

    except Exception as e:

        print("===================================")
        print("❌ ERROR GENERAL")
        print(e)
        print("===================================")

        return False

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


def verificar_usuario(correo, password):

    conexion = None
    cursor = None

    try:

        conexion = conectar()

        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT *
            FROM usuarios
            WHERE correo = %s
        """

        cursor.execute(sql, (correo,))

        usuario = cursor.fetchone()

        if usuario:

            if check_password_hash(
                usuario["password"],
                password
            ):

                print(
                    "✅ LOGIN EXITOSO PARA:",
                    usuario["nombre"]
                )

                return usuario

        print("❌ CORREO O CONTRASEÑA INCORRECTOS")

        return None

    except Exception as e:

        print("❌ ERROR EN LOGIN:")
        print(e)

        return None

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

import datetime

# --- RECUPERAR CONTRASEÑA ---

def guardar_token_recuperacion(email, token, expira_en_minutos=15):
    conexion = conectar()
    cursor = conexion.cursor()
    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=expira_en_minutos)
    
    cursor.execute("""
        UPDATE usuarios 
        SET reset_token = %s, reset_token_exp = %s 
        WHERE correo = %s
    """, (token, expiracion, email))
    
    conexion.commit()
    cursor.close()
    conexion.close()

def obtener_usuario_por_token(token):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM usuarios 
        WHERE reset_token = %s AND reset_token_exp > NOW()
    """, (token,))
    
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def actualizar_password_y_limpiar_token(usuario_id, nueva_password):
    conexion = conectar()
    cursor = conexion.cursor()
    
    # 1. Hashear la nueva contraseña antes de guardar
    password_hash = generate_password_hash(nueva_password)
    
    # 2. Corregido: 'password' en lugar de 'contraseña'
    cursor.execute("""
        UPDATE usuarios 
        SET password = %s, reset_token = NULL, reset_token_exp = NULL 
        WHERE id = %s
    """, (password_hash, usuario_id))
    
    conexion.commit()
    cursor.close()
    conexion.close()

# --- AUTENTICACIÓN EN 2 PASOS (2FA) ---

def guardar_codigo_2fa(usuario_id, codigo, expira_en_minutos=10):
    conexion = conectar()
    cursor = conexion.cursor()
    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=expira_en_minutos)
    
    cursor.execute("""
        UPDATE usuarios 
        SET codigo_2fa = %s, codigo_2fa_exp = %s 
        WHERE id = %s
    """, (codigo, expiracion, usuario_id))
    
    conexion.commit()
    cursor.close()
    conexion.close()

def verificar_codigo_2fa(usuario_id, codigo):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM usuarios 
        WHERE id = %s AND codigo_2fa = %s AND codigo_2fa_exp > NOW()
    """, (usuario_id, codigo))
    
    usuario = cursor.fetchone()
    
    if usuario:
        cursor.execute("""
            UPDATE usuarios 
            SET codigo_2fa = NULL, codigo_2fa_exp = NULL 
            WHERE id = %s
        """, (usuario_id,))
        conexion.commit()
        
    cursor.close()
    conexion.close()
    return usuario

# --- INICIALIZAR TABLA DE SERVICIOS ---

def crear_tabla_servicios():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # 1. Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Insertar registros iniciales si está vacía
        cursor.execute("SELECT COUNT(*) FROM servicios")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO servicios (nombre, descripcion) VALUES 
                ('Consulta General', 'Evaluación y diagnóstico odontológico general.'),
                ('Blanqueamiento Dental', 'Tratamiento estético para aclarar el tono dental.'),
                ('Limpieza Profiláctica', 'Limpieza profunda para remover placa y sarro.')
            """)

        conexion.commit()
        print("✅ TABLA 'servicios' VERIFICADA / CREADA CORRECTAMENTE")

    except Exception as e:
        print("❌ ERROR AL CREAR TABLA 'servicios':", e)

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Ejecutar automáticamente al importar o iniciar db.py
# crear_tabla_servicios()

def agregar_columna_servicio_id():
    conexion = None
    cursor = None
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        
        # Intentar añadir la columna servicio_id a la tabla citas
        cursor.execute("""
            ALTER TABLE citas 
            ADD COLUMN servicio_id INT NULL,
            ADD CONSTRAINT fk_citas_servicios 
            FOREIGN KEY (servicio_id) REFERENCES servicios(id) 
            ON DELETE SET NULL
        """)
        conexion.commit()
        print("✅ Columna 'servicio_id' agregada exitosamente a la tabla 'citas'")
    except mysql.connector.Error as e:
        # Si la columna ya existe (error 1060), simplemente lo ignoramos
        if e.errno == 1060:
            pass
        else:
            print("⚠️ Nota al modificar tabla citas:", e.msg)
    except Exception as e:
        print("❌ Error general al actualizar la tabla citas:", e)
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

# Ejecutar la modificación al iniciar
# agregar_columna_servicio_id()