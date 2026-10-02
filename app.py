import os
import time
import random
import secrets
import datetime
import logging
from io import BytesIO
from datetime import date
import base64
import requests
import mysql.connector

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. CARGAR VARIABLES DE ENTORNO
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# 2. CREAR INSTANCIA DE FLASK
# ---------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mi_clave_secreta_odontologia")

# ---------------------------------------------------------
# 3. IMPORTAR FUNCIONES DE BASE DE DATOS
# ---------------------------------------------------------
from db import conectar, insertar_usuario, verificar_usuario
from db import crear_tabla_servicios, agregar_columna_servicio_id

# ---------------------------------------------------------
# 4. INICIALIZACIÓN SEGURA DE LA BASE DE DATOS
# ---------------------------------------------------------
tablas_inicializadas = False

@app.before_request
def inicializar_bd_una_vez():
    global tablas_inicializadas
    if not tablas_inicializadas:
        try:
            crear_tabla_servicios()
            agregar_columna_servicio_id()
            tablas_inicializadas = True
        except Exception as e:
            print("Error al inicializar la base de datos:", e)

# ------------------------------------------------------------------------------
# CONFIGURACIÓN E INICIALIZACIÓN
# ------------------------------------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_consultorio")

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'andresbelloruiz02@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'dgmh tewn ncxu ueze')
app.config['MAIL_DEFAULT_SENDER'] = ('Consultorio Dental', os.getenv('MAIL_USERNAME', 'andresbelloruiz02@gmail.com'))

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

api_key_gemini = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key="api_key_gemini")
client = (
    genai.Client(api_key=api_key_gemini) if api_key_gemini else None
)

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')

# ------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------------------------
def verificar_recaptcha(response_token):
    payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': response_token}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    resultado = r.json()
    return resultado.get('success', False)

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

def actualizar_password_y_limpiar_token(usuario_id, nueva_password_hash):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE usuarios 
        SET contraseña = %s, reset_token = NULL, reset_token_exp = NULL 
        WHERE id = %s
    """, (nueva_password_hash, usuario_id))
    conexion.commit()
    cursor.close()
    conexion.close()

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

# ------------------------------------------------------------------------------
# RUTAS PRINCIPALES
# ------------------------------------------------------------------------------
@app.route('/')
def index():
    alerta_6m = False
    proxima = None
    opiniones = []

    if 'usuario_id' in session:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        
        # Próxima cita
        cursor.execute("""
            SELECT fecha, hora FROM citas
            WHERE usuario_id = %s AND fecha >= CURDATE()
            ORDER BY fecha ASC LIMIT 1
        """, (session['usuario_id'],))
        proxima = cursor.fetchone()

        # Última cita para alerta de 6 meses
        cursor.execute("""
            SELECT fecha FROM citas
            WHERE usuario_id = %s ORDER BY fecha DESC LIMIT 1
        """, (session['usuario_id'],))
        ultima = cursor.fetchone()

        if ultima:
            cursor.execute("SELECT DATEDIFF(CURDATE(), %s) AS dias", (ultima['fecha'],))
            resultado = cursor.fetchone()
            if resultado and resultado['dias'] >= 180:
                alerta_6m = True

        cursor.close()
        conexion.close()

    # Cargar los 6 comentarios más recientes
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT opiniones.id, opiniones.calificacion, opiniones.comentario, opiniones.fecha, usuarios.nombre
            FROM opiniones
            INNER JOIN usuarios ON opiniones.usuario_id = usuarios.id
            ORDER BY opiniones.fecha DESC
            LIMIT 6
        """)
        opiniones = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error cargando opiniones:", e)

    # El return DEBE estar al mismo nivel de sangría que el inicio del código dentro de la función
    return render_template('index.html', alerta_6m=alerta_6m, proxima=proxima, opiniones=opiniones)

@app.route('/sobre_nosotros')
def sobre_nosotros():
    return render_template('sobre_nosotros.html')

@app.route('/citas')
def citas():
    # Cargar servicios activos para mostrarlos en el formulario de citas
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicios WHERE activo = TRUE")
    servicios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('citas.html', servicios=servicios)

@app.route('/ubicacion')
def ubicacion():
    return render_template('ubicacion.html')

@app.route('/contactenos')
def contactenos():
    return render_template('contactenos.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/legales')
@app.route('/legales/<tipo>')
def legales(tipo=None):
    if tipo is None:
        tipo = request.args.get('tipo', 'privacidad')
    documentos_validos = ['privacidad', 'terminos', 'devoluciones', 'garantias', 'cookies', 'tratamiento_datos']
    if tipo in documentos_validos:
        try:
            return render_template(f'legales/{tipo}.html')
        except:
            return render_template('legales.html', tipo=tipo)
    return redirect(url_for('index'))

# ------------------------------------------------------------------------------
# AUTENTICACIÓN Y SEGURIDAD
# ------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verificar_recaptcha(recaptcha_response):
            return render_template('login.html', error="❌ Por favor, verifica el reCAPTCHA.")

        email = request.form.get('email')
        password = request.form.get('password')
        usuario = verificar_usuario(email, password)

        if usuario:
            codigo = str(random.randint(100000, 999999))
            guardar_codigo_2fa(usuario['id'], codigo)
            session['temp_usuario_id'] = usuario['id']

            # Imprime el código en la terminal para pruebas
            print(f"🔑 [DEBUG] Código 2FA generado para {usuario['correo']}: {codigo}")

            try:
                msg = Message(
                    subject="Codigo de verificacion 2FA",
                    recipients=[usuario['correo']],
                    body=f"Tu codigo de acceso es: {codigo}. Expira en 10 minutos."
                )
                mail.send(msg)
                print("✅ Correo 2FA enviado correctamente por Flask-Mail.")
            except Exception as e:
                print("❌ Error al enviar el correo 2FA:", e)

            return redirect(url_for('verificar_2fa'))
        else:
            return render_template('login.html', error="❌ Credenciales incorrectas.")

    return render_template('login.html')

@app.route('/verificar_2fa', methods=['GET', 'POST'])
def verificar_2fa():
    if 'temp_usuario_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip()
        usuario_id = session['temp_usuario_id']
        usuario = verificar_codigo_2fa(usuario_id, codigo)

        if usuario:
            session.pop('temp_usuario_id', None)
            session["usuario_id"] = usuario["id"]
            session["nombre"] = usuario["nombre"]
            session["email"] = usuario["correo"]
            session["rol"] = usuario["rol"]

            if usuario["rol"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("index"))
        else:
            return render_template('verificar_2fa.html', error="❌ Código incorrecto o expirado.")

    return render_template('verificar_2fa.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verificar_recaptcha(recaptcha_response):
            return render_template('register.html', error="❌ Por favor, verifica el reCAPTCHA.")

        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirmar = request.form.get('confirmar', '').strip()

        if not nombre or not email or not password or not confirmar:
            return render_template('register.html', error="❌ Todos los campos son obligatorios.")

        if password != confirmar:
            return render_template('register.html', error="❌ Las contraseñas no coinciden.")

        # Intentar insertar al usuario
        registrado = insertar_usuario(nombre, email, password, "paciente")
        
        if registrado:
            return redirect(url_for('login'))
        else:
            # CORRECCIÓN UI/UX: Mensaje descriptivo en lugar de "revisa logs de BD"
            return render_template('register.html', error="❌ El correo electrónico ya se encuentra registrado o no es válido.")

    return render_template('register.html')

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        # Verificar si el usuario realmente existe antes de enviar correo
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s OR email = %s", (email, email))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not usuario:
            return render_template('recuperar.html', error="❌ No existe ninguna cuenta registrada con este correo.")

        token = serializer.dumps(email, salt='recuperar-clave')
        link = url_for('restablecer_password', token=token, _external=True)

        try:
            msg = Message(
                subject="Restablecer Contraseña - Consultorio Odontológico",
                recipients=[email],
                body=f"Hola,\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{link}\n\nSi no solicitaste este cambio, ignora este correo."
            )
            mail.send(msg)
            return render_template('recuperar.html', mensaje="✅ Se ha enviado un enlace de recuperación a tu correo.")
        except Exception as e:
            print("❌ Error al enviar el correo de recuperación:", e)
            return render_template('recuperar.html', error="❌ No se pudo enviar el correo. Inténtalo más tarde.")

    return render_template('recuperar.html')

@app.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer_password(token):
    # Buscar si el token es válido en la base de datos
    usuario = obtener_usuario_por_token(token)
    
    if not usuario:
        return render_template('recuperar.html', error='❌ El enlace de recuperación es inválido o ha expirado.')

    if request.method == 'POST':
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verificar_recaptcha(recaptcha_response):
            return render_template('restablecer.html', token=token, error='Por favor, verifica el reCAPTCHA.')

        password = request.form.get('password')
        confirmar = request.form.get('confirmar')

        if password != confirmar:
            return render_template('restablecer.html', token=token, error='Las contraseñas no coinciden.')

        # Actualizar contraseña e inutilizar token usando db.py
        actualizar_password_y_limpiar_token(usuario['id'], password)

        return render_template('login.html', mensaje='✅ Contraseña actualizada con éxito. Ahora puedes iniciar sesión.')

    return render_template('restablecer.html', token=token)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ------------------------------------------------------------------------------
# GESTIÓN DE CITAS Y OPINIONES
# ------------------------------------------------------------------------------
@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    nombre = request.form.get('nombre')
    fecha_str = request.form.get('fecha')
    hora = request.form.get('hora')
    servicio_id = request.form.get('servicio_id')

    if not nombre or not fecha_str or not hora:
        return "<script>alert('❌ Por favor completa todos los campos.'); window.location.href='/citas';</script>"

    # === CORRECCIÓN AUDITORÍA: Validar que no sea fecha pasada ===
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        if fecha_obj < date.today():
            return "<script>alert('❌ No puedes agendar citas en fechas pasadas.'); window.location.href='/citas';</script>"
    except ValueError:
        return "<script>alert('❌ Formato de fecha inválido.'); window.location.href='/citas';</script>"

    conexion = None
    cursor = None

    try:
        usuario_id = session['usuario_id']
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True, buffered=True)

        cursor.execute("""
            INSERT INTO citas (usuario_id, paciente_nombre, fecha, hora, estado, servicio_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, nombre, fecha_str, hora, "Pendiente", servicio_id if servicio_id else None))

        conexion.commit()

        return "<script>alert('✅ Cita reservada correctamente.'); window.location.href='/citas';</script>"

    except mysql.connector.Error as err:
        if conexion:
            conexion.rollback()
        if err.errno == 1062:
            return "<script>alert('❌ Ese horario ya se encuentra ocupado.'); window.location.href='/citas';</script>"
        return f"<script>alert('❌ Error de BD: {err}'); window.location.href='/citas';</script>"
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


@app.route('/mis_citas')
def mis_citas():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    usuario_id = session.get('usuario_id')
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.*, s.nombre AS servicio_nombre 
        FROM citas c
        LEFT JOIN servicios s ON c.servicio_id = s.id
        WHERE c.usuario_id = %s 
        ORDER BY c.fecha DESC, c.hora DESC
    """, (usuario_id,))
    citas = cursor.fetchall()
    cursor.close()
    conexion.close()

    hoy = date.today()
    proximas = []
    pasadas = []

    for cita in citas:
        fecha_cita = cita['fecha']
        
        # === CORRECCIÓN: Convertir a date sin importar el tipo de dato ===
        if isinstance(fecha_cita, str):
            fecha_cita = datetime.strptime(fecha_cita, '%Y-%m-%d').date()
        elif isinstance(fecha_cita, datetime):
            fecha_cita = fecha_cita.date()

        if cita['estado'] == 'Completada' or fecha_cita < hoy:
            pasadas.append(cita)
        else:
            proximas.append(cita)

    return render_template('mis_citas.html', proximas=proximas, pasadas=pasadas)

@app.route('/opinion', methods=['POST'])
def opinion():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    calificacion = request.form.get('calificacion')
    comentario = request.form.get('comentario')

    if calificacion and comentario:
        try:
            calificacion = int(calificacion)
            if 1 <= calificacion <= 5:
                conexion = conectar()
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO opiniones (usuario_id, calificacion, comentario)
                    VALUES (%s, %s, %s)
                """, (session['usuario_id'], calificacion, comentario))
                conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print("Error al guardar opinión:", e)

    return redirect(url_for('index'))

# ------------------------------------------------------------------------------
# MÓDULO DE ADMINISTRACIÓN (CITAS, USUARIOS, REPORTES Y SERVICIOS)
# ------------------------------------------------------------------------------
@app.route('/admin')
def admin():
    # Verificar sesión de admin aquí según tu lógica habitual...

    # Capturar parámetros de búsqueda
    buscar_usuario = request.args.get('buscar_usuario', '').strip()
    buscar_cita = request.args.get('buscar_cita', '').strip()

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    # 1. Filtro para Usuarios
    if buscar_usuario:
        sql_usuarios = "SELECT * FROM usuarios WHERE nombre LIKE %s OR correo LIKE %s"
        cursor.execute(sql_usuarios, (f"%{buscar_usuario}%", f"%{buscar_usuario}%"))
    else:
        cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    # 2. Filtro para Citas
    if buscar_cita:
        sql_citas = """
            SELECT c.*, s.nombre AS servicio_nombre 
            FROM citas c 
            LEFT JOIN servicios s ON c.servicio_id = s.id
            WHERE c.paciente_nombre LIKE %s 
               OR s.nombre LIKE %s 
               OR c.estado LIKE %s
            ORDER BY c.fecha DESC, c.hora ASC
        """
        param = f"%{buscar_cita}%"
        cursor.execute(sql_citas, (param, param, param))
    else:
        sql_citas = """
            SELECT c.*, s.nombre AS servicio_nombre 
            FROM citas c 
            LEFT JOIN servicios s ON c.servicio_id = s.id
            ORDER BY c.fecha DESC, c.hora ASC
        """
        cursor.execute(sql_citas)
    citas = cursor.fetchall()

    # Obtener Servicios
    cursor.execute("SELECT * FROM servicios")
    servicios = cursor.fetchall()

    # Totales para tarjetas (puedes ajustar según tus consultas)
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
    total_usuarios = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM citas")
    total_citas = cursor.fetchone()['total']

    cursor.close()
    conexion.close()

    return render_template(
        'admin.html',
        usuarios=usuarios,
        citas=citas,
        servicios=servicios,
        total_usuarios=total_usuarios,
        total_citas=total_citas,
        buscar_usuario=buscar_usuario,
        buscar_cita=buscar_cita
    )

# --- RUTAS CRUD PARA SERVICIOS (PUNTO 2) ---
@app.route('/admin/crear_servicio', methods=['POST'])
def crear_servicio():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if nombre:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO servicios (nombre, descripcion, activo) VALUES (%s, %s, TRUE)", (nombre, descripcion))
        conexion.commit()
        cursor.close()
        conexion.close()

    return redirect(url_for('admin'))

@app.route('/admin/editar_servicio/<int:servicio_id>', methods=['POST'])
def editar_servicio(servicio_id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if nombre:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE servicios SET nombre = %s, descripcion = %s WHERE id = %s", (nombre, descripcion, servicio_id))
        conexion.commit()
        cursor.close()
        conexion.close()

    return redirect(url_for('admin'))

@app.route('/admin/estado_servicio/<int:servicio_id>', methods=['POST'])
def estado_servicio(servicio_id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT activo FROM servicios WHERE id = %s", (servicio_id,))
    srv = cursor.fetchone()

    if srv:
        nuevo_estado = not srv['activo']
        cursor.execute("UPDATE servicios SET activo = %s WHERE id = %s", (nuevo_estado, servicio_id))
        conexion.commit()

    cursor.close()
    conexion.close()
    return redirect(url_for('admin'))

@app.route('/admin/reportes')
def admin_reportes():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT estado, COUNT(*) as total FROM citas GROUP BY estado")
    res_estados = cursor.fetchall()

    conteo_estados = {'Pendiente': 0, 'Confirmada': 0, 'Completada': 0, 'Cancelada': 0}
    for fila in res_estados:
        if fila['estado'] in conteo_estados:
            conteo_estados[fila['estado']] = fila['total']

    cursor.execute("SELECT COUNT(*) AS total FROM citas")
    total_citas = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE rol = 'paciente'")
    total_pacientes = cursor.fetchone()['total']

    cursor.close()
    conexion.close()

    return render_template(
        'admin_reportes.html',
        estados=conteo_estados,
        total_citas=total_citas,
        total_pacientes=total_pacientes
    )

@app.route('/admin/cambiar_estado_cita/<int:cita_id>', methods=['POST'])
def cambiar_estado_cita(cita_id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    nuevo_estado = request.form.get('estado')
    estados_validos = ['Pendiente', 'Confirmada', 'Completada', 'Cancelada']

    if nuevo_estado in estados_validos:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT c.fecha, c.hora, u.nombre, u.correo 
            FROM citas c 
            JOIN usuarios u ON c.usuario_id = u.id 
            WHERE c.id = %s
        """, (cita_id,))
        cita_info = cursor.fetchone()

        cursor.execute("UPDATE citas SET estado = %s WHERE id = %s", (nuevo_estado, cita_id))
        conexion.commit()
        cursor.close()
        conexion.close()

        if cita_info and cita_info['correo']:
            try:
                paciente_nombre = cita_info['nombre']
                fecha_cita = str(cita_info['fecha'])
                hora_cita = str(cita_info['hora'])

                if nuevo_estado == 'Confirmada':
                    asunto = "Cita Confirmada - Consultorio Odontologico"
                    cuerpo = f"Hola {paciente_nombre},\n\nTu cita programada para el {fecha_cita} a las {hora_cita} ha sido CONFIRMADA.\n\n¡Te esperamos!"
                elif nuevo_estado == 'Cancelada':
                    asunto = "Cita Cancelada - Consultorio Odontologico"
                    cuerpo = f"Hola {paciente_nombre},\n\nLamentamos informarte que tu cita del {fecha_cita} a las {hora_cita} ha sido CANCELADA.\n\nPor favor contáctanos para agendar una nueva fecha."
                elif nuevo_estado == 'Completada':
                    asunto = "Cita Completada - Consultorio Odontologico"
                    cuerpo = f"Hola {paciente_nombre},\n\nGracias por tu visita. Tu cita del {fecha_cita} ha sido marcada como COMPLETADA.\n\n¡Esperamos que tu atención haya sido excelente!"
                else:
                    asunto = "Actualizacion del estado de tu cita"
                    cuerpo = f"Hola {paciente_nombre},\n\nEl estado de tu cita para el {fecha_cita} a las {hora_cita} ha cambiado a: {nuevo_estado}."

                msg = Message(subject=asunto, recipients=[cita_info['correo']], body=cuerpo)
                mail.send(msg)
            except Exception as e:
                print(f"❌ Error al enviar notificación por correo: {e}")

    return redirect(url_for('admin'))

@app.route('/admin/cambiar_rol/<int:usuario_id>', methods=['POST'])
def cambiar_rol(usuario_id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))

    nuevo_rol = request.form.get('rol')
    if nuevo_rol in ['paciente', 'admin']:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET rol = %s WHERE id = %s", (nuevo_rol, usuario_id))
        conexion.commit()
        cursor.close()
        conexion.close()

    return redirect(url_for('admin'))

@app.route('/eliminar_opinion/<int:id>', methods=['POST'])
def eliminar_opinion(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('index'))

    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM opiniones WHERE id = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error al eliminar opinión:", e)

    return redirect(url_for('index'))

# ------------------------------------------------------------------------------
# SMILEVISION: EDICIÓN DE FOTOGRAFÍAS
# ------------------------------------------------------------------------------
import re
from PIL import Image, ImageOps, UnidentifiedImageError

PROMPT_BASE = """
Edita la fotografía adjunta para crear una simulación estética fotorrealista.
Conserva la identidad, el encuadre, la perspectiva, los labios, la piel,
la iluminación y el fondo de la fotografía original.
Limita los cambios a los elementos dentales necesarios para la solicitud.
Respeta las sombras, reflejos, textura y oclusiones de la fotografía.
No añadas textos, diagramas, etiquetas, comparaciones ni marcos.
Devuelve una sola fotografía editada.

Si la boca no se distingue o la intervención solicitada es ambigua,
responde únicamente con texto explicando que hace falta otra fotografía
o una indicación más precisa. No inventes una sonrisa distinta.
"""

PROMPTS_TRATAMIENTO = {
    "ortodoncia": """
Añade brackets metálicos fotorrealistas sobre los dientes visibles.
Adapta individualmente la escala, orientación y perspectiva de cada bracket
a la superficie del diente correspondiente.
Representa el arco siguiendo la curvatura de la dentadura.
Respeta las zonas ocultas por labios y dientes.
No coloques brackets sobre encías ni dentro de espacios sin dientes.
Conserva la posición actual y el color de los dientes:
la imagen representa la colocación del aparato, no el final del tratamiento.
Usa reflejos metálicos y sombras de contacto sutiles.
""",
    "implantes": """
Simula la restauración visible del espacio dental indicado por el usuario.
Representa una corona de aspecto natural integrada con los dientes vecinos,
respetando su tamaño, forma, tono, translucidez, perspectiva e iluminación.
Conserva los demás dientes y el contorno de los labios.
No muestres tornillos, cirugía, sangre ni cortes anatómicos.
No añadas dientes en otras zonas.
Si el espacio indicado no puede identificarse con claridad, devuelve
únicamente texto solicitando una fotografía o indicación más precisa.
""",
    "blanqueamiento": """
Aclara moderadamente el tono de los dientes visibles.
Conserva sus variaciones naturales, textura y translucidez.
No aclares la piel, las encías, los labios ni el fondo.
No cambies la forma ni la posición de los dientes.
""",
    "diseno": """
Realiza una simulación estética conservadora de los dientes visibles.
Mejora de forma sutil sus contornos y uniformidad de tono.
Mantén proporciones naturales y la identidad de la sonrisa.
No añadas piezas dentales ni modifiques labios, piel o fondo.
"""
}


@app.route('/analizar_sonrisa', methods=['POST'])
def analizar_sonrisa():
    if client is None:
        return jsonify({
            "status": "error",
            "message": "Configura GEMINI_API_KEY en el archivo .env."
        }), 503

    fotografia = request.files.get("fotografia")
    tratamiento = request.form.get("tratamiento", "")
    zona_implante = request.form.get("zona_implante", "").strip()
    color = request.form.get("color_brackets", "#38bdf8")

    if not fotografia or tratamiento not in PROMPTS_TRATAMIENTO:
        return jsonify({
            "status": "error",
            "message": "Selecciona una fotografía y un tratamiento válido."
        }), 400

    if tratamiento == "implantes" and not zona_implante:
        return jsonify({
            "status": "error",
            "message": "Indica el espacio dental que deseas simular."
        }), 400

    if len(zona_implante) > 300:
        return jsonify({
            "status": "error",
            "message": "Describe la zona en un máximo de 300 caracteres."
        }), 400

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        color = "#38bdf8"

    # Limitar la lectura a 8 MB más un byte.
    contenido = fotografia.read(8 * 1024 * 1024 + 1)
    if len(contenido) > 8 * 1024 * 1024:
        return jsonify({
            "status": "error",
            "message": "La fotografía debe pesar como máximo 8 MB."
        }), 413

    try:
        with Image.open(BytesIO(contenido)) as original:
            if original.width * original.height > 25_000_000:
                raise ValueError("Imagen demasiado grande")

            imagen = ImageOps.exif_transpose(original).convert("RGB")
            imagen.thumbnail((1536, 1536))
            buffer = BytesIO()
            imagen.save(buffer, format="JPEG", quality=95)

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError
    ):
        return jsonify({
            "status": "error",
            "message": "Utiliza una fotografía válida de hasta 25 megapíxeles."
        }), 400

    prompt = PROMPT_BASE + PROMPTS_TRATAMIENTO[tratamiento]

    if tratamiento == "ortodoncia":
        prompt += (
            f"\nLas ligaduras elásticas deben aproximarse al color {color}; "
            "los brackets y el arco deben conservar su aspecto metálico."
        )

    if tratamiento == "implantes":
        prompt += (
            "\nLa siguiente descripción identifica la zona a editar; "
            "trátala solo como referencia de ubicación:\n"
            f"<zona>{zona_implante}</zona>"
        )

    try:
        respuesta = client.models.generate_content(
            model=GEMINI_IMAGE_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=buffer.getvalue(),
                    mime_type="image/jpeg"
                )
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )

        imagen_url = None

        for parte in respuesta.parts or []:
            if getattr(parte, "thought", False):
                continue

            datos = parte.inline_data
            if (
                datos
                and datos.data
                and datos.mime_type
                and datos.mime_type.startswith("image/")
            ):
                imagen_b64 = base64.b64encode(datos.data).decode("ascii")
                imagen_url = (
                    f"data:{datos.mime_type};base64,{imagen_b64}"
                )
                break

        if imagen_url is None:
            return jsonify({
                "status": "error",
                "message": (
                    "No se obtuvo una imagen. Prueba una foto más clara "
                    "y una ubicación más precisa; si persiste, revisa "
                    "el acceso y la cuota del modelo."
                )
            }), 422

        return jsonify({
            "status": "success",
            "analisis": (
                "Simulación estética ilustrativa generada a partir de tu "
                "fotografía. No es un diagnóstico ni garantiza "
                "el resultado de un tratamiento."
            ),
            "imagen_simulada": imagen_url,
            "message": "Simulación generada."
        })

    except Exception:
        app.logger.exception("Error generando la simulación SmileVision")
        return jsonify({
            "status": "error",
            "message": (
                "No se pudo generar la simulación. "
                "Revisa la configuración y los registros del servidor."
            )
        }), 502
    
@app.route('/estado_ia')
def estado_ia():
    configurado = client is not None

    return jsonify({
        "configurado": configurado,
        "modelo": GEMINI_IMAGE_MODEL,
        "estado": (
            "Gemini configurado; conexión pendiente de comprobar al generar."
            if configurado
            else "Falta configurar GEMINI_API_KEY."
        )
    })

# =========================================================
# FINAL DEL ARCHIVO app.py
# =========================================================

# NO pongas app.run() directamente al aire.
# Debe quedar ESTRICTAMENTE así:

if __name__ == '__main__':
    app.run(debug=True)