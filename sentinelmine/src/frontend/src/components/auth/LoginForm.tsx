import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  IconButton,
  useToast,
  Heading,
  Checkbox,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';

// Types
interface LoginFormData {
  username: string;
  password: string;
  rememberMe: boolean;
}

// Component
const LoginForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showMfa, setShowMfa] = useState(false);
  const [mfaToken, setMfaToken] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const toast = useToast();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const {
    handleSubmit,
    register,
    formState: { errors },
  } = useForm<LoginFormData>();

  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  const handleLogin = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // In a real app, you would use your auth service to login
      // const response = await authService.login(data.username, data.password);

      // Simulate MFA required
      setShowMfa(true);
      setMfaToken('mfa-token-123456');
      setIsLoading(false);

      // If MFA is not required, this would handle the login success
      // dispatch login success action
      // navigate('/dashboard');
    } catch (error) {
      setIsLoading(false);
      toast({
        title: 'Login Failed',
        description: 'Invalid username or password',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleVerifyMfa = async () => {
    try {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // In a real app, you would verify the MFA code
      // const response = await authService.verifyMfa(mfaToken, otpCode);

      setIsLoading(false);
      toast({
        title: 'Login Successful',
        description: 'Welcome to SentinelMine',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // dispatch login success action
      dispatch({ type: 'auth/loginSuccess', payload: { 
        user: {
          id: 'user-001',
          username: 'john.analyst',
          fullName: 'John Analyst',
          role: 'analyst',
          department: 'intelligence',
          securityClearance: 'top_secret'
        },
        token: 'sample-jwt-token'
      }});

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      setIsLoading(false);
      toast({
        title: 'Verification Failed',
        description: 'Invalid verification code',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  if (showMfa) {
    return (
      <Box w="100%" maxW="400px" p={8} borderRadius="md" boxShadow="lg" bg="white">
        <VStack spacing={4} align="flex-start">
          <Heading size="lg">Two-Factor Authentication</Heading>
          <Text>Enter the 6-digit code from your authenticator app.</Text>
          <FormControl isRequired>
            <FormLabel>Verification Code</FormLabel>
            <Input
              type="text"
              placeholder="Enter 6-digit code"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              maxLength={6}
            />
          </FormControl>
          <Button
            colorScheme="blue"
            width="full"
            onClick={handleVerifyMfa}
            isLoading={isLoading}
            loadingText="Verifying"
          >
            Verify
          </Button>
        </VStack>
      </Box>
    );
  }

  return (
    <Box w="100%" maxW="400px" p={8} borderRadius="md" boxShadow="lg" bg="white">
      <form onSubmit={handleSubmit(handleLogin)}>
        <VStack spacing={4} align="flex-start">
          <Heading size="lg">Sign In</Heading>
          <Text>Enter your credentials to access the system.</Text>

          <FormControl isInvalid={!!errors.username} isRequired>
            <FormLabel>Username</FormLabel>
            <Input
              type="text"
              placeholder="Enter your username"
              {...register('username', { required: 'Username is required' })}
            />
            <FormErrorMessage>{errors.username?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={!!errors.password} isRequired>
            <FormLabel>Password</FormLabel>
            <InputGroup>
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                {...register('password', { required: 'Password is required' })}
              />
              <InputRightElement>
                <IconButton
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                  onClick={togglePasswordVisibility}
                  variant="ghost"
                  size="sm"
                />
              </InputRightElement>
            </InputGroup>
            <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
          </FormControl>

          <FormControl>
            <Checkbox {...register('rememberMe')}>Remember me</Checkbox>
          </FormControl>

          <Button
            colorScheme="blue"
            width="full"
            type="submit"
            isLoading={isLoading}
            loadingText="Signing In"
          >
            Sign In
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default LoginForm; 