import numpy as np
import random

# --- ML Model Implementation ---
class SimpleAnomalyDetector:
    def __init__(self, sensor='moisture', method='threshold', window=10):
        self.sensor = sensor
        self.method = method
        self.window = window
        self.history = []
        if method == 'threshold':
            # basic, hardcoded thresholds per type
            self.limits = {
                'moisture': (25, 85),
                'temperature': (7, 41),
                'humidity': (25, 95),
            }

    def step(self, value):
        if self.method == 'threshold':
            lower, upper = self.limits[self.sensor]
            return value < lower or value > upper
        elif self.method == 'rolling':
            self.history.append(value)
            if len(self.history) > self.window:
                self.history.pop(0)
            if len(self.history) < self.window:
                return False  # not enough data
            mean = np.mean(self.history)
            std = np.std(self.history)
            # flag as anomaly if outside mean +/- 2.5 stddev
            return abs(value - mean) > 2.5 * std
        return False

# --- Synthetic test run (example) ---
def test():
    values = [random.uniform(35, 75) for _ in range(25)]  # normal values
    values += [10, 95, 5]  # injected anomalies

    detector = SimpleAnomalyDetector(sensor='moisture', method='rolling', window=10)
    print("Testing rolling stats anomaly detector:")
    for i, v in enumerate(values):
        if detector.step(v):
            print(f"Anomaly at {i}: value={v}, window={detector.history}")

    detector2 = SimpleAnomalyDetector(sensor='moisture', method='threshold')
    print("\nTesting threshold anomaly detector:")
    for i, v in enumerate(values):
        if detector2.step(v):
            print(f"Anomaly at {i}: value={v}")

if __name__ == "__main__":
    test()
