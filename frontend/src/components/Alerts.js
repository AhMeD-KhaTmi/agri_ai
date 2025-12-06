import React, { useState, useEffect } from 'react';
import { anomalyAPI, recommendationAPI } from '../services/api';
import './Alerts.css';

const Alerts = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const [anomaliesRes, recommendationsRes] = await Promise.all([
        anomalyAPI.list(),
        recommendationAPI.list(),
      ]);
      setAnomalies(anomaliesRes.data);
      setRecommendations(recommendationsRes.data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      // Set empty arrays on error to prevent crash
      setAnomalies([]);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationForAnomaly = (anomalyId) => {
    return recommendations.find(r => r.anomaly_event === anomalyId);
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#3498db';
      default: return '#95a5a6';
    }
  };

  if (loading) {
    return <div className="alerts-loading">Loading alerts...</div>;
  }

  return (
    <div className="alerts">
      <h1>🚨 Anomaly Alerts & Recommendations</h1>
      {anomalies.length === 0 ? (
        <div className="no-alerts">No anomalies detected. All systems normal! ✅</div>
      ) : (
        <div className="alerts-list">
          {anomalies.map(anomaly => {
            const recommendation = getRecommendationForAnomaly(anomaly.id);
            return (
              <div key={anomaly.id} className="alert-card">
                <div className="alert-header">
                  <h3>{anomaly.anomaly_type}</h3>
                  <span
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(anomaly.severity) }}
                  >
                    {anomaly.severity?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
                <div className="alert-details">
                  <p><strong>Plot ID:</strong> {anomaly.plot}</p>
                  <p><strong>Detected:</strong> {new Date(anomaly.timestamp).toLocaleString()}</p>
                  <p><strong>Confidence:</strong> {(anomaly.model_confidence * 100).toFixed(1)}%</p>
                </div>
                {recommendation && (
                  <div className="recommendation-box">
                    <h4>🤖 AI Recommendation</h4>
                    <p className="recommendation-action"><strong>Action:</strong> {recommendation.recommended_action}</p>
                    <p className="recommendation-explanation">{recommendation.explanation_text}</p>
                    <span className="confidence-tag">Confidence: {recommendation.confidence}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Alerts;

