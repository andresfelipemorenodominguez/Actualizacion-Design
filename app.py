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

    html = f"""
    <html>
      <body style="margin:0; padding:0; background-color:#f0f7ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        
        <table width="100%" cellpadding="0" cellspacing="0" style="padding: 30px 0;">
          <tr>
            <td align="center">

              <table cellpadding="0" cellspacing="0" width="480" 
                     style="background:#ffffff; border-radius:10px; padding:30px;
                            box-shadow:0 8px 25px rgba(0,51,102,0.15);
                            border:1px solid #CCCCCC;">

                <!-- TÍTULO -->
                <tr>
                  <td style="text-align:center; padding-bottom:20px;">
                    <h1 style="color:#003366; font-size:24px; margin:0;">
                      Verificación de cuenta
                    </h1>
                    <p style="color:#666; font-size:14px; margin-top:8px;">
                      Tu código de verificación está listo
                    </p>
                  </td>
                </tr>

                <!-- CÓDIGO -->
                <tr>
                  <td style="padding:20px 0; text-align:center;">
                    <div style="
                        background:#f8fafc;
                        border:1px solid #CCCCCC;
                        border-radius:8px;
                        font-size:32px;
                        font-weight:bold;
                        color:#4A90E2;
                        padding:15px 0;">
                      🔐 {codigo}
                    </div>
                  </td>
                </tr>

                <!-- TEXTO FINAL -->
                <tr>
                  <td style="padding-top:20px; text-align:center;">
                    <p style="color:#003366; font-size:15px; margin:0 20px;">
                      Ingresa este código en la página de verificación para activar tu cuenta.
                    </p>

                    <p style="font-size:12px; color:#666; margin-top:25px;">
                      Si no solicitaste este código, simplemente ignora este mensaje.
                    </p>
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>

      </body>
    </html>
    """

    mensaje = MIMEText(html, "html")
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
    return render_template("loginadmin.html")

# -------------------------
# MAIN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
