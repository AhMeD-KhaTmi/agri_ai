#!/usr/bin/env python
"""
Quick test script for anomaly detection
Run this to test the updated ML model with specification-based thresholds
"""
import requests
import sys

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"

def get_token(username, password):
    """Get JWT token"""
    response = requests.post(TOKEN_URL, data={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_anomaly(headers, plot_id, sensor_type, value, expected_anomaly):
    """Test a single anomaly case"""
    print(f"\n🧪 Testing: {sensor_type} = {value}")
    print(f"   Expected: {expected_anomaly}")
    
    response = requests.post(API_URL, json={
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": value
    }, headers=headers)
    
    if response.status_code == 201:
        print(f"   ✅ Reading created (Status: {response.status_code})")
        print(f"   📋 Check Django admin or frontend for anomaly detection")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        return False

def main():
    print("=" * 60)
    print("🧪 Anomaly Detection Test Script")
    print("=" * 60)
    
    # Get credentials
    username = input("\nEnter username: ").strip()
    password = input("Enter password: ").strip()
    plot_id = input("Enter plot ID (e.g., 1): ").strip()
    
    try:
        plot_id = int(plot_id)
    except ValueError:
        print("❌ Invalid plot ID. Using default: 1")
        plot_id = 1
    
    # Authenticate
    print("\n🔐 Authenticating...")
    token = get_token(username, password)
    if not token:
        print("❌ Authentication failed. Exiting.")
        sys.exit(1)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Authentication successful!")
    
    # Test cases based on specification
    print("\n" + "=" * 60)
    print("Running Test Cases...")
    print("=" * 60)
    
    tests = [
        # Threshold violations
        (plot_id, "moisture", 30, "Low moisture (<35%)"),
        (plot_id, "moisture", 80, "High moisture (>75%)"),
        (plot_id, "temperature", 35, "Heat stress (>32°C)"),
        (plot_id, "temperature", 8, "Cold stress (<10°C)"),
        (plot_id, "humidity", 25, "Dry conditions (<30%)"),
        (plot_id, "humidity", 90, "Excessive moisture (>85%)"),
        
        # Normal values (should NOT trigger anomalies)
        (plot_id, "moisture", 60, "Normal (no anomaly expected)"),
        (plot_id, "temperature", 22, "Normal (no anomaly expected)"),
        (plot_id, "humidity", 65, "Normal (no anomaly expected)"),
    ]
    
    passed = 0
    failed = 0
    
    for plot, sensor, value, expected in tests:
        success = test_anomaly(headers, plot, sensor, value, expected)
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    print("\n" + "=" * 60)
    print("📋 Next Steps:")
    print("=" * 60)
    print("1. Check Django admin: http://127.0.0.1:8000/admin")
    print("   - Look at 'Anomaly Events' for detected anomalies")
    print("   - Look at 'Agent Recommendations' for AI suggestions")
    print("\n2. Check Frontend: http://localhost:3000")
    print("   - Go to 'Alerts' page to see anomalies")
    print("   - Check 'Dashboard' for plot status indicators")
    print("\n3. Check Django server logs for:")
    print("   - '🚨 ANOMALY DETECTED' messages")
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()

