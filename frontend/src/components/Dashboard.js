import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { anomalyAPI, plotsAPI } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [plots, setPlots] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch plots and anomalies
      const [plotsRes, anomaliesRes] = await Promise.all([
        plotsAPI.list(),
        anomalyAPI.list().catch(() => ({ data: [] })) // If no permission, return empty
      ]);
      
      setAnomalies(anomaliesRes.data || []);
      setPlots(plotsRes.data || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      // If plots fail, try to fetch anyway
      try {
        const plotsRes = await plotsAPI.list();
        setPlots(plotsRes.data || []);
      } catch (plotErr) {
        console.error('Error fetching plots:', plotErr);
      }
    } finally {
      setLoading(false);
    }
  };

  const getPlotStatus = (plotId) => {
    const plotAnomalies = anomalies.filter(a => a.plot === plotId);
    if (plotAnomalies.length === 0) return 'healthy';
    if (plotAnomalies.some(a => a.severity === 'high')) return 'critical';
    return 'warning';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#27ae60';
      case 'warning': return '#f39c12';
      case 'critical': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Farm Dashboard</h1>
      <div className="plots-grid">
        {plots.length === 0 ? (
          <div className="no-plots">
            <p>No plots available. Create plots in Django admin first.</p>
          </div>
        ) : (
          plots.map(plot => {
            const status = getPlotStatus(plot.id);
            const anomalyCount = anomalies.filter(a => a.plot === plot.id).length;
            return (
              <Link key={plot.id} to={`/plot/${plot.id}`} className="plot-card">
                <div className="plot-header">
                  <h3>{plot.name}</h3>
                  <span 
                    className="status-indicator" 
                    style={{ backgroundColor: getStatusColor(status) }}
                  >
                    {status.toUpperCase()}
                  </span>
                </div>
                <div className="plot-info">
                  <p><strong>Crop:</strong> {plot.crop_variety}</p>
                  <p><strong>Location:</strong> {plot.farm_location || 'N/A'}</p>
                  <p><strong>Anomalies:</strong> {anomalyCount}</p>
                </div>
              </Link>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Dashboard;

