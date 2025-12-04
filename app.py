from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "clave-super-secreta"

# -------------------------
# CONFIGURACIÓN DE EMAIL
# -------------------------
EMAIL_USER = "miboletin5@gmail.com"   # <<--- CAMBIA ESTO
EMAIL_PASSWORD = "ubzg mvmd gxbe laah"  # <<--- CAMBIA ESTO


# -------------------------
# FUNCIÓN DE ENVÍO DE CORREO
# -------------------------
def enviar_correo_verificacion(destinatario, codigo):
    mensaje = MIMEText(f"""
    Hola, tu código de verificación es:

        🔐 {codigo}

    Ingresa este código en la página de verificación para activar tu cuenta.
    """)
    mensaje["Subject"] = "Código de verificación - Plataforma Educativa"
    mensaje["From"] = EMAIL_USER
    mensaje["To"] = destinatario

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_USER, EMAIL_PASSWORD)
        servidor.sendmail(EMAIL_USER, destinatario, mensaje.as_string())
        servidor.quit()
        print("Correo enviado correctamente.")
        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False


# -------------------------
# CONEXIÓN A POSTGRESQL
# -------------------------
def conexion_bd():
    return psycopg2.connect(
        host="localhost",
        database="miboletin",
        user="postgres",
        password="123456"
    )


# -------------------------
# RUTA PRINCIPAL: REGISTRO
# -------------------------
@app.route('/')
def index():
    return render_template("register.html")


# -------------------------
# PROCESAR REGISTRO
# -------------------------
@app.route('/registro', methods=['POST'])
def registro():
    nombre_completo = request.form['nombre_completo']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    confirmar = request.form['confirmar_contrasena']

    # Validar contraseñas
    if contrasena != confirmar:
        flash("Las contraseñas no coinciden")
        return redirect(url_for('index'))

    try:
        conn = conexion_bd()
        cursor = conn.cursor()

        # Guardar usuario en BD
        cursor.execute("""
            INSERT INTO administradores (nombre_completo, correo_electronico, contrasena)
            VALUES (%s, %s, %s)
        """, (nombre_completo, correo, contrasena))

        conn.commit()
        cursor.close()
        conn.close()

        # Guardar información de usuario
        session['correo_registrado'] = correo
        session['nombre_registrado'] = nombre_completo

        # Generar código de verificación
        codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
        session['codigo_verificacion'] = codigo

        # Enviar correo
        enviar_correo_verificacion(correo, codigo)

        return redirect(url_for('verificacion_correo'))

    except Exception as e:
        flash(f"Error al registrar: {e}")
        return redirect(url_for('index'))


# -------------------------
# MOSTRAR PÁGINA DE VERIFICACIÓN
# -------------------------
@app.route('/verificacion-correo')
def verificacion_correo():
    correo = session.get('correo_registrado', '')
    return render_template("verificacioncorreo.html", correo=correo)


# -------------------------
# VALIDAR CÓDIGO INGRESADO
# -------------------------
@app.route('/admin_validate_code', methods=['POST'])
def admin_validate_code():
    codigo_ingresado = request.form.get('codigo')
    codigo_correcto = session.get('codigo_verificacion')

    if codigo_ingresado == codigo_correcto:
        flash("Correo verificado correctamente")

        # Borrar el código por seguridad
        session.pop('codigo_verificacion', None)

        return redirect(url_for('admin_login'))
    else:
        flash("Código incorrecto, intenta de nuevo")
        return redirect(url_for('verificacion_correo'))


# -------------------------
# REENVIAR CÓDIGO
# -------------------------
@app.route('/admin_resend_code')
def admin_resend_code():
    correo = session.get('correo_registrado')

    # Nuevo código
    nuevo_codigo = "".join([str(random.randint(0, 9)) for _ in range(6)])
    session['codigo_verificacion'] = nuevo_codigo

    enviar_correo_verificacion(correo, nuevo_codigo)

    flash("Nuevo código enviado a tu correo")
    return redirect(url_for('verificacion_correo'))


# -------------------------
# LOGIN (AÚN EN PLANTILLA)
# -------------------------
@app.route('/admin_login')
def admin_login():
    return "Página de login - Pendiente de implementar"


# -------------------------
# MAIN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
