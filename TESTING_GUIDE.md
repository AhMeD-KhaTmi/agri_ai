# 🧪 Testing Guide - Updated ML Model

## Quick Test Methods

### **Method 1: Use the Simulator (Easiest)**

The simulator will automatically generate data and trigger anomalies.

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Run simulator with anomaly injection:**
   ```bash
   cd simulator
   python simulator.py --plots 1 --freq 5 --inject_anomaly --anomaly_every 3 --username your_username
   ```
   (Replace `your_username` with your actual username)

3. **Watch the output** - You should see:
   - ✅ Successful sensor readings
   - 🚨 Anomaly detection messages
   - Status codes 201 for successful posts

4. **Check results:**
   - Open frontend: http://localhost:3000
   - Go to **Alerts page** - You should see anomalies!
   - Check **Dashboard** - Plots should show warning/critical status

---

### **Method 2: Test Specific Anomaly Types Manually**

#### **Test 1: Low Moisture Threshold (<35%)**
1. Go to Django Admin: http://127.0.0.1:8000/admin
2. Navigate to **Sensor Readings** → **Add Sensor Reading**
3. Create reading:
   - Plot: Select any plot
   - Sensor type: `moisture`
   - Value: `30` (below 35% threshold)
   - Save
4. **Expected:** Should create anomaly "Low moisture (<35%)"

#### **Test 2: Heat Stress (>32°C)**
1. Add Sensor Reading:
   - Plot: Select any plot
   - Sensor type: `temperature`
   - Value: `35` (above 32°C)
   - Save
2. **Expected:** Should create anomaly "Heat stress (>32°C sustained)"

#### **Test 3: Sudden Drop (>10% in 1-3 hours)**
This requires multiple readings over time:

1. **First reading (baseline):**
   - Plot: Same plot (e.g., Plot ID 1)
   - Sensor type: `moisture`
   - Value: `60`
   - Save
   - **Wait 2 minutes** (or manually change timestamp in admin)

2. **Second reading (sudden drop):**
   - Plot: Same plot
   - Sensor type: `moisture`
   - Value: `45` (60 - 45 = 15% drop, >10%)
   - **Important:** In Django admin, you can't easily change timestamp, so:
     - Either use the simulator (it creates realistic timestamps)
     - Or create readings via API with custom timestamps

3. **Expected:** Should detect "Sudden moisture drop (15.0% in 1-3h)"

---

### **Method 3: Test via API (Postman/curl)**

#### **Test Threshold Violations:**

**Low Moisture:**
```bash
curl -X POST http://127.0.0.1:8000/api/sensor-readings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plot": 1,
    "sensor_type": "moisture",
    "value": 30
  }'
```

**Heat Stress:**
```bash
curl -X POST http://127.0.0.1:8000/api/sensor-readings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plot": 1,
    "sensor_type": "temperature",
    "value": 35
  }'
```

**Dry Conditions (Low Humidity):**
```bash
curl -X POST http://127.0.0.1:8000/api/sensor-readings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plot": 1,
    "sensor_type": "humidity",
    "value": 25
  }'
```

---

### **Method 4: Check Django Server Logs**

When anomalies are detected, you'll see in your Django terminal:

```
🚨 ANOMALY DETECTED: Low moisture (<35%) (Severity: high, Confidence: 0.85)
```

or

```
🚨 ANOMALY DETECTED: Sudden moisture drop (15.0% in 1-3h) (Severity: high, Confidence: 0.95)
```

---

### **Method 5: Verify in Frontend**

1. **Dashboard:**
   - Status indicators should change to warning/critical
   - Plots with anomalies show red/yellow badges

2. **Alerts Page:**
   - Should list all detected anomalies
   - Shows severity badges (high/medium/low)
   - Displays AI recommendations for each anomaly

3. **Plot Detail Page:**
   - Charts should show the anomalous values
   - You can see the spike/drop in the time-series

---

### **Method 6: Check Database Directly**

1. Django Admin → **Anomaly Events**
   - Should see new records with correct:
     - `anomaly_type` (e.g., "Low moisture (<35%)")
     - `severity` (high/medium/low)
     - `model_confidence` (0.80-0.95)

2. Django Admin → **Agent Recommendations**
   - Should see recommendations linked to anomalies
   - `recommended_action` and `explanation_text` populated

---

## **Testing Checklist**

### ✅ Threshold Tests
- [ ] Low moisture (<35%) triggers anomaly
- [ ] High temperature (>32°C) triggers heat stress
- [ ] Low temperature (<10°C) triggers cold stress
- [ ] Low humidity (<30%) triggers dry conditions
- [ ] High humidity (>85%) triggers excessive moisture

### ✅ Advanced Detection Tests
- [ ] Sudden drop detection (>10% in 1-3 hours)
- [ ] Data drift detection (>20% over 24-48h)

### ✅ Frontend Tests
- [ ] Anomalies appear in Alerts page
- [ ] Recommendations display correctly
- [ ] Dashboard shows status indicators
- [ ] Charts display anomalous data points

---

## **Quick Test Script**

You can also create a Python script to test:

```python
# test_anomalies.py
import requests
import time

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test 1: Low moisture
print("Test 1: Low moisture...")
response = requests.post(API_URL, json={
    "plot": 1,
    "sensor_type": "moisture",
    "value": 30
}, headers=headers)
print(f"Status: {response.status_code}")

# Test 2: Heat stress
print("\nTest 2: Heat stress...")
response = requests.post(API_URL, json={
    "plot": 1,
    "sensor_type": "temperature",
    "value": 35
}, headers=headers)
print(f"Status: {response.status_code}")

# Test 3: Dry conditions
print("\nTest 3: Dry conditions...")
response = requests.post(API_URL, json={
    "plot": 1,
    "sensor_type": "humidity",
    "value": 25
}, headers=headers)
print(f"Status: {response.status_code}")

print("\n✅ Tests completed! Check Django admin or frontend for anomalies.")
```

---

## **What to Look For**

✅ **Success Indicators:**
- Django logs show "🚨 ANOMALY DETECTED" messages
- Anomaly Events created in database
- Recommendations generated automatically
- Frontend displays anomalies correctly
- Correct severity levels assigned

❌ **If Something's Wrong:**
- Check Django server logs for errors
- Verify you have plots in the database
- Ensure JWT token is valid
- Check that sensor readings are being created

---

**Ready to test! Start with Method 1 (simulator) for the easiest testing experience.**

