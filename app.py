from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = "clave-super-secreta"  # Necesario para mensajes flash

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
    nombre = request.form['nombre_completo']
    correo = request.form['correo']
    telefono = request.form['telefono']
    contrasena = request.form['contrasena']
    confirmar = request.form['confirmar_contrasena']

    # Validación de contraseña
    if contrasena != confirmar:
        flash("Las contraseñas no coinciden")
        return redirect(url_for('index'))

    try:
        conn = conexion_bd()
        cursor = conn.cursor()

        # Inserción a la tabla administradores
        cursor.execute("""
            INSERT INTO administradores (nombre_completo, correo, telefono, contrasena)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, telefono, contrasena))  

        conn.commit()
        cursor.close()
        conn.close()

        flash("Registro exitoso")
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error: {e}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
