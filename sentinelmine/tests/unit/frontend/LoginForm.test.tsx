import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import LoginForm from '../../../src/frontend/src/components/auth/LoginForm';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../../../src/frontend/src/store/slices/authSlice';

// Mock the axios instance
jest.mock('axios', () => ({
  post: jest.fn(),
}));

// Create test store with auth reducer
const createTestStore = () => 
  configureStore({
    reducer: {
      auth: authReducer
    }
  });

describe('LoginForm Component', () => {
  let store;
  
  beforeEach(() => {
    store = createTestStore();
    // Clear mock calls between tests
    jest.clearAllMocks();
  });
  
  test('renders login form correctly', () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ChakraProvider>
            <LoginForm />
          </ChakraProvider>
        </BrowserRouter>
      </Provider>
    );
    
    // Check if important elements are rendered
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
  
  test('handles input changes', () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ChakraProvider>
            <LoginForm />
          </ChakraProvider>
        </BrowserRouter>
      </Provider>
    );
    
    // Find input elements
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    // Simulate user input
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    // Check if values were updated
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });
  
  test('displays validation errors for empty submission', async () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ChakraProvider>
            <LoginForm />
          </ChakraProvider>
        </BrowserRouter>
      </Provider>
    );
    
    // Find and click submit button without entering data
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    // Wait for validation errors to appear
    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('calls login action when form is submitted with valid data', async () => {
    const axios = require('axios');
    axios.post.mockResolvedValueOnce({ 
      data: { 
        token: 'test-token',
        user: { id: 1, username: 'testuser' }
      } 
    });

    render(
      <Provider store={store}>
        <BrowserRouter>
          <ChakraProvider>
            <LoginForm />
          </ChakraProvider>
        </BrowserRouter>
      </Provider>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'testuser' } 
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'password123' } 
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify that the API was called with correct data
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'), 
        { username: 'testuser', password: 'password123' }
      );
    });

    // Check that the store was updated with the user details
    await waitFor(() => {
      const state = store.getState();
      expect(state.auth.isAuthenticated).toBe(true);
      expect(state.auth.user).toEqual({ id: 1, username: 'testuser' });
      expect(state.auth.token).toBe('test-token');
    });
  });

  it('displays an error message when login fails', async () => {
    const axios = require('axios');
    axios.post.mockRejectedValueOnce({ 
      response: { 
        data: { message: 'Invalid credentials' } 
      } 
    });

    render(
      <Provider store={store}>
        <BrowserRouter>
          <ChakraProvider>
            <LoginForm />
          </ChakraProvider>
        </BrowserRouter>
      </Provider>
    );

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/username/i), { 
      target: { value: 'testuser' } 
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), { 
      target: { value: 'wrongpassword' } 
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify the error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });

    // Check that the store was not updated
    await waitFor(() => {
      const state = store.getState();
      expect(state.auth.isAuthenticated).toBe(false);
      expect(state.auth.user).toBeNull();
    });
  });
}); 