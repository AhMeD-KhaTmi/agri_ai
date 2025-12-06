import React from 'react';
import { Navigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const ProtectedRoute = ({ children }) => {
  const token = authAPI.getToken();
  return token ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;

