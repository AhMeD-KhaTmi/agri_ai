import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api, { authAPI } from '../services/api';
import './Signup.css';

const Signup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'farmer'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await api.post('/register/', formData);
      console.log('Registration successful:', response.data);
      // After successful registration, automatically log in
      await authAPI.login(formData.username, formData.password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
      console.error('Error response:', err.response?.data);
      
      // Better error handling
      let errorMsg = 'Registration failed. Please try again.';
      
      if (err.response?.data) {
        const data = err.response.data;
        // Handle field-specific errors
        if (data.username) {
          errorMsg = `Username: ${Array.isArray(data.username) ? data.username[0] : data.username}`;
        } else if (data.password) {
          errorMsg = `Password: ${Array.isArray(data.password) ? data.password[0] : data.password}`;
        } else if (data.email) {
          errorMsg = `Email: ${Array.isArray(data.email) ? data.email[0] : data.email}`;
        } else if (data.detail) {
          errorMsg = data.detail;
        } else if (data.non_field_errors) {
          errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
        } else {
          // Try to format all errors
          const errorList = Object.keys(data).map(key => {
            const value = data[key];
            return `${key}: ${Array.isArray(value) ? value[0] : value}`;
          }).join(', ');
          if (errorList) errorMsg = errorList;
        }
      } else if (err.message) {
        errorMsg = err.message;
      } else if (!err.response) {
        errorMsg = 'Cannot connect to server. Make sure Django backend is running on http://127.0.0.1:8000';
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        <h2>🌾 Create Account</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label>Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="farmer">Farmer</option>
              <option value="admin">Admin</option>
            </select>
            <small style={{ color: '#666', fontSize: '0.85rem', marginTop: '0.5rem', display: 'block' }}>
              Note: Admin role should be assigned by existing admins
            </small>
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading} className="signup-btn">
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
          <div className="login-link">
            Already have an account? <Link to="/login">Login here</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Signup;

