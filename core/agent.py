def generate_recommendation(anomaly_type, sensor_type, value=None):
    """
    Given anomaly_type/sensor_type (and optionally value), return
    (recommended_action:str, explanation:str)
    Uses specification-based rules for recommendations.
    """
    anomaly_lower = anomaly_type.lower() if anomaly_type else ""
    
    # Handle sudden drops (critical - possible irrigation failure)
    if "sudden" in anomaly_lower and "drop" in anomaly_lower:
        return (
            "Check irrigation system immediately",
            "Sudden moisture drop detected (>10% in 1-3 hours). Possible irrigation failure or leak. Inspect irrigation equipment and water supply."
        )
    
    # Handle low moisture
    if "low moisture" in anomaly_lower or ("moisture" in anomaly_lower and ("<35" in anomaly_type or "below" in anomaly_lower)):
        return (
            "Irrigate field",
            "Soil moisture is below optimal range (<35%). Initiate irrigation to restore adequate moisture for crop health."
        )
    
    # Handle high moisture
    if "high moisture" in anomaly_lower or ("moisture" in anomaly_lower and ">" in anomaly_type):
        return (
            "Check drainage system",
            "Soil moisture is excessively high. Check drainage and avoid overwatering to prevent root rot."
        )
    
    # Handle heat stress
    if "heat stress" in anomaly_lower or ("temperature" in anomaly_lower and ">32" in anomaly_type):
        return (
            "Activate shade or cooling",
            "Temperature exceeds safe threshold (>32°C sustained). Use shade nets, misting, or cooling methods to prevent crop heat stress and reduce transpiration loss."
        )
    
    # Handle cold stress
    if "cold stress" in anomaly_lower or ("temperature" in anomaly_lower and "<10" in anomaly_type):
        return (
            "Protect from cold",
            "Temperature is below minimum threshold (<10°C). Use frost protection, covers, or heating to prevent cold damage to crops."
        )
    
    # Handle temperature out of range
    if "temperature" in anomaly_lower and "out of normal" in anomaly_lower:
        return (
            "Monitor and adjust climate controls",
            "Temperature is outside optimal range (18-28°C). Adjust climate control systems to maintain optimal growing conditions."
        )
    
    # Handle dry conditions (low humidity)
    if "dry conditions" in anomaly_lower or ("humidity" in anomaly_lower and "<30" in anomaly_type):
        return (
            "Increase humidity or misting",
            "Humidity is below optimal range (<30%). Use misting, irrigation, or humidity controls to increase air moisture around crops."
        )
    
    # Handle excessive moisture (high humidity)
    if "excessive moisture" in anomaly_lower or ("humidity" in anomaly_lower and ">85" in anomaly_type):
        return (
            "Improve ventilation",
            "Humidity is excessively high (>85%). Improve air circulation and ventilation to prevent fungal diseases and mold growth."
        )
    
    # Handle data drift
    if "drift" in anomaly_lower:
        direction = "increasing" if "increase" in anomaly_lower else "decreasing"
        return (
            "Investigate gradual trend change",
            f"Detected gradual {direction} trend (>20% over 24-48h). This may indicate systematic changes in environmental conditions or sensor calibration issues. Review sensor accuracy and environmental factors."
        )
    
    # Fallback for other anomaly types
    if "moisture" in anomaly_lower:
        return (
            "Check irrigation system",
            "Moisture anomaly detected. Inspect irrigation equipment, check soil conditions, and verify sensor readings."
        )
    if "temperature" in anomaly_lower:
        return (
            "Adjust climate controls",
            "Temperature anomaly detected. Review climate control systems and environmental conditions."
        )
    if "humidity" in anomaly_lower:
        return (
            "Adjust humidity controls",
            "Humidity anomaly detected. Review ventilation and humidity management systems."
        )
    
    return (
        "Monitor field closely",
        "Anomaly detected. Continue monitoring conditions and investigate potential environmental or equipment issues."
    )
