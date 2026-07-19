import os
import datetime
import csv
from flask import Flask, request, render_template
from prettytable import PrettyTable
from colorama import init, Fore, Style
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
init(autoreset=True)

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DB = os.getenv("MYSQL_DB", "sensor_esp")
MYSQL_USER = os.getenv("MYSQL_USER", "dba_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

if not MYSQL_PASSWORD:
    print("[WARN] MYSQL_PASSWORD no está definida. Conectando sin contraseña.")
    print("[WARN] Define MYSQL_PASSWORD en .env para producción.")


def read_csv_data(filename):
    try:
        with open(f'data/{filename}', 'r') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def save_to_csv(data, filename):
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'a', newline='') as csvfile:
        fieldnames = ['Sensor', 'Temperatura (°C)', 'Humedad (%)', 'Fecha']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


def save_to_db(data, table_name):
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            database=MYSQL_DB,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        if connection.is_connected():
            cursor = connection.cursor()
            allowed_tables = {"datos_sensor_dht22", "datos_sensor_dht11"}
            if table_name not in allowed_tables:
                raise ValueError(f"Table {table_name} not allowed")
            insert_query = f"INSERT INTO {table_name} (fecha, temperatura, humedad) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (data['Fecha'], data['Temperatura (°C)'], data['Humedad (%)']))
            connection.commit()
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return False


@app.route('/datos_sensor/', methods=['POST'])
def datos_sensor():
    if request.method == 'POST':
        data = request.json
        print(data)

        if 'temperatura_dht22' not in data or 'humedad_dht22' not in data or 'temperatura_dht11' not in data or 'humedad_dht11' not in data:
            return 'Datos incompletos', 400

        fecha_hora_actual = datetime.datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")

        temperatura_dht22 = data['temperatura_dht22']
        humedad_dht22 = data['humedad_dht22']
        temperatura_dht11 = data['temperatura_dht11']
        humedad_dht11 = data['humedad_dht11']

        table = PrettyTable()
        table.field_names = [Fore.BLUE + 'Sensor', Fore.BLUE + 'Temperatura (°C)', Fore.BLUE + 'Humedad (%)' + Style.RESET_ALL]
        table.add_row(['Exterior', f'{Fore.GREEN}{temperatura_dht22:.1f}', f'{Fore.GREEN}{humedad_dht22:.1f}' + Style.RESET_ALL])
        table.add_row(['Interior', f'{Fore.CYAN}{temperatura_dht11:.1f}', f'{Fore.CYAN}{humedad_dht11:.1f}' + Style.RESET_ALL])
        print(table)

        data_dht22 = {
            'Sensor': 'Exterior',
            'Temperatura (°C)': temperatura_dht22,
            'Humedad (%)': humedad_dht22,
            'Fecha': fecha_hora_formateada
        }

        data_dht11 = {
            'Sensor': 'Interior',
            'Temperatura (°C)': temperatura_dht11,
            'Humedad (%)': humedad_dht11,
            'Fecha': fecha_hora_formateada
        }

        if not save_to_db(data_dht22, 'datos_sensor_dht22'):
            save_to_csv(data_dht22, 'datos_sensor_dht22_backup.csv')

        if not save_to_db(data_dht11, 'datos_sensor_dht11'):
            save_to_csv(data_dht11, 'datos_sensor_dht11_backup.csv')

        return 'Datos recibidos y almacenados con éxito.'


@app.route('/')
def index():
    data_dht22 = read_csv_data('datos_sensor_dht22.csv')
    data_dht11 = read_csv_data('datos_sensor_dht11.csv')
    return render_template('index.html', data_dht22=data_dht22, data_dht11=data_dht11)


if __name__ == '__main__':
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))
    app.run(host=host, port=port, debug=False)
