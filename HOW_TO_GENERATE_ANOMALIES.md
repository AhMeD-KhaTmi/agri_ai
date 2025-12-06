# How to Generate Anomalies & Test the System

## Why No Anomalies?

Anomalies are automatically created when:
1. Sensor readings are sent to the API
2. The ML model detects abnormal values (too low/high)
3. An AnomalyEvent is created and linked to an AgentRecommendation

**Currently, you have no anomalies because no sensor data has been sent yet!**

---

## Method 1: Use the Simulator (Recommended)

This is the easiest way to generate realistic sensor data with anomalies.

### Step 1: Get Your JWT Token

You need to get a token for a user with "farmer" role:

1. Log in via the frontend (or use Postman)
2. Check browser localStorage: `localStorage.getItem('access_token')`
3. Copy the token

### Step 2: Run the Simulator

```bash
# From project root
cd simulator
python simulator.py --plots 1 2 --freq 3 --inject_anomaly --anomaly_every 4 --token YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual JWT token.

This will:
- Send sensor readings for plots 1 and 2
- Inject anomalies every 4th reading
- Trigger the ML anomaly detection
- Create AnomalyEvents and Recommendations automatically

### Step 3: Check Dashboard

Refresh your frontend dashboard and alerts page - you should see:
- Status indicators on plots (warning/critical)
- Anomaly alerts with recommendations

---

## Method 2: Manual API Testing (Postman/curl)

### Send a Normal Reading (No Anomaly)
```bash
curl -X POST http://127.0.0.1:8000/api/sensor-readings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plot": 1,
    "sensor_type": "moisture",
    "value": 60.0
  }'
```

### Send an Anomalous Reading (Will Create Anomaly)
```bash
curl -X POST http://127.0.0.1:8000/api/sensor-readings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plot": 1,
    "sensor_type": "moisture",
    "value": 10.0
  }'
```

This low moisture value will trigger:
- ML anomaly detection
- AnomalyEvent creation
- Automatic AgentRecommendation generation

---

## Method 3: Create Test Data via Django Admin

1. Go to http://127.0.0.1:8000/admin
2. Navigate to "Sensor Readings"
3. Add a reading with:
   - Plot: Select one of your plots
   - Sensor type: moisture/temperature/humidity
   - Value: Use extreme values to trigger anomalies:
     - Moisture: < 25 (low) or > 85 (high)
     - Temperature: < 7 (low) or > 41 (high)
     - Humidity: < 25 (low) or > 95 (high)
4. Save - this will automatically trigger anomaly detection!

---

## What Happens Automatically

When you send sensor readings:
1. ✅ Reading is saved to database
2. ✅ ML model analyzes the value (threshold + rolling stats)
3. ✅ If anomaly detected → AnomalyEvent created
4. ✅ AI Agent generates recommendation → AgentRecommendation created
5. ✅ Frontend dashboard/alerts update automatically

---

## Troubleshooting

**Still no anomalies after sending data?**
- Check Django server logs for errors
- Verify plot ID exists in database
- Check user has permission (farmer/agent/admin role)
- Verify ML model thresholds are correct

**Want to see anomalies immediately?**
- Use the simulator with `--inject_anomaly` flag
- Send readings with extreme values (very low/high)

