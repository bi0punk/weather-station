# Weather Station

Consolidated temperature and humidity monitoring system. Receives data from DHT22/DHT11 sensors (via ESP32/Arduino HTTP POST), stores it in MySQL with CSV fallback, and provides a web UI.

**Security:** Debug mode disabled by default. SQL injection prevented via table name whitelist.

## Features

- Dual sensor support (DHT22 exterior, DHT11 interior)
- MySQL storage with automatic CSV fallback
- Web UI with DataTables (sorting, searching, pagination)
- PrettyTable console output with colorama
- SQLite-based alternative dashboard (`routes.py`)
- Arduino firmware included (`sensor.ino`)

## Stack

Python 3, Flask, MySQL, SQLite (optional), PrettyTable, Colorama

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MySQL credentials
python app.py
```

Open `http://localhost:8000` for the web dashboard.

## Configuration

Create `.env` from `.env.example`:

| Variable | Default | Description |
|---|---|---|
| `MYSQL_HOST` | `localhost` | MySQL server host |
| `MYSQL_DB` | `sensor_esp` | Database name |
| `MYSQL_USER` | `dba_user` | Database user |
| `MYSQL_PASSWORD` | — | Database password |

## API

- `POST /datos_sensor/` — Receive sensor JSON data (DHT22 + DHT11)
- `GET /` — Web UI to view sensor data

## Database Setup

```sql
CREATE DATABASE sensor_esp;
CREATE TABLE datos_sensor_dht22 (id INT AUTO_INCREMENT PRIMARY KEY, fecha DATETIME, temperatura FLOAT, humedad FLOAT);
CREATE TABLE datos_sensor_dht11 (id INT AUTO_INCREMENT PRIMARY KEY, fecha DATETIME, temperatura FLOAT, humedad FLOAT);
```

Only `datos_sensor_dht22` and `datos_sensor_dht11` tables are allowed (whitelist enforced).

## Security

- **Debug mode:** Disabled by default. Set `DEBUG=true` env var for development.
- **SQL injection:** Table names are validated against an allowlist.
- **MySQL credentials:** Read from environment variables only, not hardcoded.

## Alternative: SQLite (routes.py)

```bash
python routes.py
```

This starts a simpler dashboard that receives single temperature readings via `POST /sensor` and stores them in SQLite.

## License

MIT
