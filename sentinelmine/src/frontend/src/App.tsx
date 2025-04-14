import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider, Box } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Provider } from 'react-redux';

// Store
import { store } from './store';

// Theme and styles
import theme from './utils/theme';

// Components
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Pages
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import PredictionsPage from './pages/predictions/PredictionsPage';
import PredictionDetailPage from './pages/predictions/PredictionDetailPage';
import CreatePredictionPage from './pages/predictions/CreatePredictionPage';
import AlertsPage from './pages/alerts/AlertsPage';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import UserProfilePage from './pages/users/UserProfilePage';
import SettingsPage from './pages/settings/SettingsPage';
import NotFoundPage from './pages/errors/NotFoundPage';

// Initialize React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ChakraProvider theme={theme}>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected routes - wrapped in Layout */}
              <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/predictions" element={<PredictionsPage />} />
                <Route path="/predictions/create" element={<CreatePredictionPage />} />
                <Route path="/predictions/:id" element={<PredictionDetailPage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/profile" element={<UserProfilePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
              
              {/* 404 Page */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Router>
        </ChakraProvider>
      </QueryClientProvider>
    </Provider>
  );
}

export default App; 