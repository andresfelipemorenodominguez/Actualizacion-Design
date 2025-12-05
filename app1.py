from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

# Ruta principal que muestra login.html
@app.route('/')
def index():
    return render_template('login.html')

# Ruta para manejar el inicio de sesión (POST)
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        
        # Aquí deberías verificar las credenciales en tu base de datos
        # Por ahora, solo mostraremos un mensaje de éxito
        flash(f'Inicio de sesión exitoso para: {correo}', 'success')
        
        # Redirigir a una página de dashboard después del login
        # return redirect(url_for('dashboard'))
        return f'Login exitoso para: {correo}. ¡Esta sería la página de dashboard!'

# Ruta para la página de recuperación de contraseña
@app.route('/forgot_password')
def forgot_password():
    return 'Página de recuperación de contraseña (pendiente de implementar)'

# Ejemplo de otras rutas que podrías necesitar
@app.route('/dashboard')
def dashboard():
    return 'Página principal del sistema (dashboard)'

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)