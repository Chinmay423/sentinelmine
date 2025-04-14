import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import LoginForm from '../../../src/frontend/src/components/auth/LoginForm';

const mockStore = configureStore([]);

describe('LoginForm Component', () => {
  let store;
  
  beforeEach(() => {
    store = mockStore({
      auth: {
        isLoading: false,
        error: null
      }
    });
    
    store.dispatch = jest.fn();
  });
  
  test('should render login form correctly', () => {
    render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
  
  test('should dispatch login action when form is submitted', () => {
    render(
      <Provider store={store}>
        <LoginForm />
      </Provider>
    );
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'analyst@example.gov' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'SecurePassword123!' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    expect(store.dispatch).toHaveBeenCalledWith(
      expect.objectContaining({
        type: expect.stringContaining('auth/login')
      })
    );
  });
}); 