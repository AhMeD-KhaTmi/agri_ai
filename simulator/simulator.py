import time
import random
import requests
import math
import argparse

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"

# Argument parsing
parser = argparse.ArgumentParser(description="Agri AI Sensor Data Simulator")
parser.add_argument("--plots", type=int, nargs='+', default=[1], help="List of plot IDs to simulate")
parser.add_argument("--freq", type=float, default=5, help="Frequency (in seconds) between data sends")
parser.add_argument("--inject_anomaly", action="store_true", help="Inject anomalies periodically for testing")
parser.add_argument("--anomaly_every", type=int, default=5, help="On average, inject 1 anomaly every N readings per sensor")
parser.add_argument("--token", type=str, help="JWT token for Authorization header (optional if using --username)")
parser.add_argument("--username", type=str, help="Username to auto-login and get token")
parser.add_argument("--password", type=str, help="Password for auto-login (optional, will prompt if not provided)")
args = parser.parse_args()

# Auto-fetch token if username provided
token = args.token
if not token and args.username:
    print("🔐 Authenticating...")
    password = args.password or input(f"Enter password for {args.username}: ")
    try:
        form_data = {
            'username': args.username,
            'password': password
        }
        response = requests.post(TOKEN_URL, data=form_data)
        if response.status_code == 200:
            token = response.json()['access']
            print("✅ Authentication successful!")
        else:
            print(f"❌ Authentication failed: {response.text}")
            exit(1)
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        exit(1)
elif not token:
    print("⚠️  No token provided. Use --token or --username to authenticate.")
    print("   The simulator will run but API calls will fail without authentication.")

PLOT_IDS = args.plots
SEND_INTERVAL = args.freq

print(f"\n🚀 Starting simulator for plots: {PLOT_IDS}")
print(f"   Frequency: {SEND_INTERVAL}s between sends")
if args.inject_anomaly:
    print(f"   ⚠️  Anomaly injection: ON (avg 1 anomaly every {args.anomaly_every} readings per sensor)")
print()

start_time = time.time()

def send_data(sensor_type, value, plot_id):
    payload = {
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": value
    }
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        status_emoji = "✅" if response.status_code in [200, 201] else "⚠️"
        print(f"{status_emoji} plot={plot_id}, {sensor_type} = {value} → {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️  Authentication failed. Check your token/credentials")
    except Exception as e:
        print(f"❌ Error: {e}")

# Functions with diurnal/gradual/cyclic patterns:
def diurnal_cycle(t, min_v, max_v, period=24*60*60):
    # Simulate 24h sine wave
    amp = (max_v - min_v) / 2
    base = (max_v + min_v) / 2
    return base + amp * math.sin(2 * math.pi * t / period)

def moisture_pattern(t):
    # Moisture can dip midday and rise at night (simulate evapotranspiration cycle)
    noise = random.uniform(-2, 2)
    return round(diurnal_cycle(t, 30, 80) + noise, 2)

def temperature_pattern(t):
    noise = random.uniform(-1, 1)
    return round(diurnal_cycle(t, 13, 39) + noise, 2)

def humidity_pattern(t):
    # Humidity peaks at dawn and drops in afternoon
    noise = random.uniform(-3, 3)
    return round(80 - diurnal_cycle(t, 10, 35) + noise, 2)

def inject_anomaly(sensor_type, normal_value):
    """Return an anomalous value for the given sensor."""
    if sensor_type == "moisture":
        # Randomly choose between very low or very high moisture
        return random.choice([15, 95])
    if sensor_type == "temperature":
        # Abnormally high or low temperature
        return random.choice([5, 45])
    if sensor_type == "humidity":
        # Abnormally low or high humidity
        return random.choice([20, 95])
    return normal_value

# Per-reading anomaly probability derived from anomaly_every
anomaly_probability = 1.0 / max(args.anomaly_every, 1)

while True:
    now = time.time() - start_time
    for pid in PLOT_IDS:
        for sensor_type, pattern_func in [
            ("moisture", moisture_pattern),
            ("temperature", temperature_pattern),
            ("humidity", humidity_pattern),
        ]:
            v = pattern_func(now)
            # Independent random anomaly decision per (plot, sensor) reading
            if args.inject_anomaly and random.random() < anomaly_probability:
                v = inject_anomaly(sensor_type, v)
            send_data(sensor_type, v, pid)
    time.sleep(SEND_INTERVAL)
