from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'Pardo@28062000'
#Session(app)

# Datos de conexión a la base de datos
db_params = {
    'dbname': 'BDProyectoIS',
    'user': 'postgres',
    'password': 'Pardo@2000',
    'host': 'localhost',
    'port': '5432',
}
#cadena de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Pardo@2000@34.67.56.45:5432/BDProyectoIS'
db = SQLAlchemy(app)
def login(username, password):
    try:
        # Establecer conexión a la base de datos
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Consulta SQL para verificar el inicio de sesión
        query = "SELECT codigo FROM login WHERE usuario = %s AND clave = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        if result:
            return True  # Las credenciales son correctas, el inicio de sesión es exitoso
        else:
            return False  # Las credenciales son incorrectas

    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/verificar_login', methods=['POST'])
def verificar_login():
    username = request.form['username']
    password = request.form['password']

    if login(username, password):
        # Si las credenciales son correctas, establece una sesión y redirige al usuario a la página de éxito
        session['username'] = username
        return redirect('/Menu')
    else:
        # Si las credenciales son incorrectas, muestra un mensaje de error y redirige al usuario nuevamente al formulario
        flash('Usuario o contraseña incorrectos.', 'error')
        return redirect('/')

@app.route('/Menu')
def login_exitoso():
    # Verifica si el usuario tiene una sesión activa
    if 'username' in session:
        return render_template('Menu.html', username=session['username'])
    else:
        return redirect('/')

def obtener_datos(tabla):
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        consulta = "SELECT * FROM productos"
        cursor.execute(consulta)
        data = cursor.fetchall()

        cursor.close()
        connection.close()

        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)

        return df

    except Exception as e:
        print("Error al obtener datos:", str(e))
        return None

@app.route('/ver-productos')
def ver_productos():
    # Obtener los datos de la tabla de productos
    datos_productos = obtener_datos('productos')

    if datos_productos is not None:
        return render_template('productos.html', datos_productos=datos_productos)
    else:
        return 'Error al obtener datos de productos'

@app.route('/guardar_producto', methods=['GET', 'POST'])
def guardar_producto():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre_producto = request.form['nombre_producto']
        peso = request.form['peso']
        volumen = request.form['volumen']

        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            # Inserta los datos en la tabla 'productos'
            cursor.execute("INSERT INTO productos (codigo, nombre_producto, peso, volumen) VALUES (%s, %s, %s, %s)",
                           (codigo, nombre_producto, peso, volumen))
            connection.commit()

            cursor.close()
            connection.close()

            flash('Producto ingresado exitosamente.', 'success')
            return redirect(url_for('guardar_producto'))

        except Exception as e:
            flash('Error al ingresar producto.', 'error')
            return redirect(url_for('guardar_producto'))

    return render_template('guardar_producto.html')

def obtener_productos():
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        consulta = "SELECT DISTINCT nombre_producto FROM productos"
        cursor.execute(consulta)
        productos = cursor.fetchall()

        cursor.close()
        connection.close()

        # Formatea los resultados como una lista de nombres de productos
        lista_productos = [producto[0] for producto in productos]

        return lista_productos

    except Exception as e:
        print("Error al obtener datos de productos:", str(e))
        return []

def obtener_sensores():
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        consulta = "SELECT DISTINCT nombre_sensor FROM sensores"
        cursor.execute(consulta)
        sensores = cursor.fetchall()

        cursor.close()
        connection.close()

        # Formatea los resultados como una lista de nombres de sensores
        lista_sensores = [sensor[0] for sensor in sensores]

        return lista_sensores

    except Exception as e:
        print("Error al obtener datos de sensores:", str(e))
        return []

@app.route('/ingresar_control', methods=['GET', 'POST'])
def ingresar_control():
    if request.method == 'POST':
        producto = request.form['producto']
        sensor = request.form['sensor']
        temp_max = request.form['temp_max']
        temp_min = request.form['temp_min']
        temp_recibida = request.form['temp_recibida']

        try:
            connection = psycopg2.connect(**db_params)
            cursor = connection.cursor()

            # Inserta los datos en la tabla 'Control_Temp'
            cursor.execute("INSERT INTO Control_Temp (producto, sensor, temp_max, temp_min, temp_recibida) VALUES (%s, %s, %s, %s, %s)",
                           (producto, sensor, temp_max, temp_min, temp_recibida))
            connection.commit()

            cursor.close()
            connection.close()

            flash('Control de temperatura ingresado exitosamente.', 'success')
            return redirect(url_for('ingresar_control'))

        except Exception as e:
            flash('Error al ingresar control de temperatura.', 'error')
            return redirect(url_for('ingresar_control'))

    # Obtener la lista de productos y sensores
    productos = obtener_productos()
    sensores = obtener_sensores()

    if productos and sensores:
        return render_template('control_temp.html', productos=productos, sensores=sensores)
    else:
        return 'Error al obtener datos de productos y sensores'



@app.route('/grafica')
def grafica():
    try:
        connection = psycopg2.connect(**db_params)
        consulta = """
            SELECT producto, temp_recibida, temp_max, temp_min
            FROM Control_Temp
        """
        df = pd.read_sql_query(consulta, connection)
        connection.close()

        # Crear la gráfica de líneas
        fig = px.line(df, x='producto', y=['temp_recibida', 'temp_max', 'temp_min'], title='Gráfica de Temperaturas por Producto')

        # Convierte la gráfica en JSON
        graphJSON = fig.to_json()

        return render_template('grafica.html', graphJSON=graphJSON)

    except Exception as e:
        print("Error al obtener datos y crear la gráfica:", str(e))
        return 'Error al obtener datos de temperatura'


if __name__ == "__main__":
    app.run(debug=True)