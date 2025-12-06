import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { sensorAPI } from '../services/api';
import './PlotDetail.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const PlotDetail = () => {
  const { plotId } = useParams();
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sensorType, setSensorType] = useState('moisture');

  useEffect(() => {
    fetchReadings();
  }, [plotId, sensorType]);

  const fetchReadings = async () => {
    try {
      const response = await sensorAPI.list(plotId);
      const filtered = response.data.filter(r => r.sensor_type === sensorType);
      setReadings(filtered);
    } catch (err) {
      console.error('Error fetching readings:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: readings.map(r => new Date(r.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: sensorType.charAt(0).toUpperCase() + sensorType.slice(1),
        data: readings.map(r => r.value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${sensorType.charAt(0).toUpperCase() + sensorType.slice(1)} Over Time`,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  if (loading) {
    return <div className="plot-detail-loading">Loading plot data...</div>;
  }

  return (
    <div className="plot-detail">
      <h1>Plot {plotId} Details</h1>
      <div className="sensor-selector">
        <button
          onClick={() => setSensorType('moisture')}
          className={sensorType === 'moisture' ? 'active' : ''}
        >
          Moisture
        </button>
        <button
          onClick={() => setSensorType('temperature')}
          className={sensorType === 'temperature' ? 'active' : ''}
        >
          Temperature
        </button>
        <button
          onClick={() => setSensorType('humidity')}
          className={sensorType === 'humidity' ? 'active' : ''}
        >
          Humidity
        </button>
      </div>
      <div className="chart-container">
        {readings.length > 0 ? (
          <Line data={chartData} options={chartOptions} />
        ) : (
          <div className="no-data">No {sensorType} data available for this plot.</div>
        )}
      </div>
    </div>
  );
};

export default PlotDetail;

