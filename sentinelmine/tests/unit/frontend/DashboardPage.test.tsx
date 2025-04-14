import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ChakraProvider } from '@chakra-ui/react';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../../../src/frontend/src/pages/dashboard/DashboardPage';
import authSlice from '../../../src/frontend/src/store/slices/authSlice';
import * as predictionService from '../../../src/frontend/src/services/predictionService';

// Mock the prediction service
jest.mock('../../../src/frontend/src/services/predictionService');

// Create a mock store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice.reducer,
    },
    preloadedState: initialState
  });
};

describe('DashboardPage Component', () => {
  let store;

  beforeEach(() => {
    store = createMockStore({
      auth: {
        isAuthenticated: true,
        user: { id: 1, username: 'testuser', role: 'analyst' },
        token: 'test-token'
      }
    });

    // Mock the prediction service
    jest.spyOn(predictionService, 'getPredictions').mockResolvedValue({
      data: [
        { id: 1, type: 'activity', prediction: 'Suspicious Activity', confidence: 0.85, timestamp: '2023-05-10T10:00:00Z' },
        { id: 2, type: 'threat', prediction: 'Potential Breach', confidence: 0.72, timestamp: '2023-05-10T11:30:00Z' }
      ]
    });

    jest.spyOn(predictionService, 'getThreatMetrics').mockResolvedValue({
      data: {
        totalThreats: 47,
        criticalThreats: 5,
        resolvedThreats: 32,
        averageResolutionTime: '3.5 hours',
        threatsByCategory: {
          'Malware': 18,
          'Phishing': 12,
          'Unauthorized Access': 10,
          'Data Breach': 7
        }
      }
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders dashboard with title and metric cards', async () => {
    render(
      <Provider store={store}>
        <ChakraProvider>
          <BrowserRouter>
            <DashboardPage />
          </BrowserRouter>
        </ChakraProvider>
      </Provider>
    );

    // Check for dashboard title
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    
    // Wait for metric cards to load
    await waitFor(() => {
      expect(screen.getByText(/total threats/i)).toBeInTheDocument();
      expect(screen.getByText(/critical threats/i)).toBeInTheDocument();
    });
    
    // Verify metrics content
    await waitFor(() => {
      expect(screen.getByText('47')).toBeInTheDocument();  // Total threats
      expect(screen.getByText('5')).toBeInTheDocument();   // Critical threats
      expect(screen.getByText('32')).toBeInTheDocument();  // Resolved threats
    });
  });

  it('calls prediction service when dashboard loads', async () => {
    render(
      <Provider store={store}>
        <ChakraProvider>
          <BrowserRouter>
            <DashboardPage />
          </BrowserRouter>
        </ChakraProvider>
      </Provider>
    );

    // Verify that the prediction service was called
    await waitFor(() => {
      expect(predictionService.getPredictions).toHaveBeenCalled();
      expect(predictionService.getThreatMetrics).toHaveBeenCalled();
    });
  });

  it('displays recent predictions in the table', async () => {
    render(
      <Provider store={store}>
        <ChakraProvider>
          <BrowserRouter>
            <DashboardPage />
          </BrowserRouter>
        </ChakraProvider>
      </Provider>
    );
    
    // Check for prediction table data
    await waitFor(() => {
      expect(screen.getByText('Suspicious Activity')).toBeInTheDocument();
      expect(screen.getByText('Potential Breach')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument(); // 0.85 confidence as percentage
    });
  });
}); 