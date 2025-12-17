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

  const getChartColors = (type) => {
    const colors = {
      moisture: {
        border: 'rgb(102, 126, 234)',
        background: 'rgba(102, 126, 234, 0.1)',
      },
      temperature: {
        border: 'rgb(230, 76, 60)',
        background: 'rgba(230, 76, 60, 0.1)',
      },
      humidity: {
        border: 'rgb(39, 174, 96)',
        background: 'rgba(39, 174, 96, 0.1)',
      },
    };
    return colors[type] || colors.moisture;
  };

  const chartColors = getChartColors(sensorType);

  const chartData = {
    labels: readings.map(r => new Date(r.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: sensorType.charAt(0).toUpperCase() + sensorType.slice(1),
        data: readings.map(r => r.value),
        borderColor: chartColors.border,
        backgroundColor: chartColors.background,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: chartColors.border,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            weight: '600',
          },
          padding: 20,
        },
      },
      title: {
        display: true,
        text: `${sensorType.charAt(0).toUpperCase() + sensorType.slice(1)} Over Time`,
        font: {
          size: 18,
          weight: '700',
        },
        color: '#2c3e50',
        padding: {
          top: 10,
          bottom: 30,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: '600',
        },
        bodyFont: {
          size: 13,
        },
        borderColor: chartColors.border,
        borderWidth: 2,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          font: {
            size: 12,
          },
        },
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          font: {
            size: 12,
          },
        },
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

