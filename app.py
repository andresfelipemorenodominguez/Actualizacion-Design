from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.secret_key = "clave-super-secreta"

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
# RUTA PRINCIPAL (MUESTRA REGISTER)
# -------------------------
@app.route('/')
def index():
    return render_template("register.html")

# -------------------------
# RUTA QUE RECIBE EL FORMULARIO
# -------------------------
@app.route('/registro', methods=['POST'])
def registro():
    nombre_completo = request.form['nombre_completo']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    confirmar = request.form['confirmar_contrasena']

    # Validación de contraseña
    if contrasena != confirmar:
        flash("Las contraseñas no coinciden")
        return redirect(url_for('index'))

    try:
        conn = conexion_bd()
        cursor = conn.cursor()

        # Inserción a la tabla administradores SIN apellido
        cursor.execute("""
            INSERT INTO administradores (nombre_completo, correo_electronico, contrasena)
            VALUES (%s, %s, %s)
        """, (nombre_completo, correo, contrasena))

        conn.commit()
        cursor.close()
        conn.close()

        # Guardar el correo en sesión para usarlo en la verificación
        session['correo_registrado'] = correo
        session['nombre_registrado'] = nombre_completo
        
        # Redirigir a la página de verificación en lugar de mostrar flash
        return redirect(url_for('verificacion_correo'))

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('index'))

# -------------------------
# NUEVA RUTA PARA VERIFICACIÓN DE CORREO
# -------------------------
@app.route('/verificacion-correo')
def verificacion_correo():
    # Obtener el correo de la sesión
    correo = session.get('correo_registrado', '')
    
    # Pasar el correo a la plantilla si lo necesitas mostrar
    return render_template("verificacioncorreo.html", correo=correo)

# -------------------------
# RUTA PARA PROCESAR EL CÓDIGO DE VERIFICACIÓN
# -------------------------
@app.route('/admin_validate_code', methods=['POST'])
def admin_validate_code():
    codigo = request.form.get('codigo')
    
    # Aquí deberías:
    # 1. Verificar el código ingresado
    # 2. Si es correcto, marcar el correo como verificado en la BD
    # 3. Redirigir a la página de login o dashboard
    
    # Por ahora, solo mostramos un mensaje
    flash(f"Código ingresado: {codigo}")
    
    # Redirigir al login después de la verificación
    return redirect(url_for('admin_login'))

# -------------------------
# RUTA PARA REENVIAR CÓDIGO
# -------------------------
@app.route('/admin_resend_code')
def admin_resend_code():
    # Aquí implementarías la lógica para reenviar el código
    flash("Código reenviado")
    return redirect(url_for('verificacion_correo'))

# -------------------------
# RUTA DE LOGIN (EJEMPLO)
# -------------------------
@app.route('/admin_login')
def admin_login():
    return "Página de login - Pendiente de implementar"

if __name__ == '__main__':
    app.run(debug=True)