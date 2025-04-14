import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

interface ProtectedRouteProps {
  children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation();
  
  // In a real app, you would use a selector to get auth state from Redux
  // const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  
  // For demo purposes, we'll simulate authentication
  const isAuthenticated = true; // This would be dynamically pulled from Redux
  
  if (!isAuthenticated) {
    // Redirect to login page but save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};

export default ProtectedRoute; 