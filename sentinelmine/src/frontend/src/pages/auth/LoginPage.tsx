import React from 'react';
import { Box, Flex, Text, Image, useColorModeValue, Heading } from '@chakra-ui/react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

// Components
import LoginForm from '../../components/auth/LoginForm';

// Store selectors
const selectIsAuthenticated = (state: any) => state.auth?.isAuthenticated;

const LoginPage: React.FC = () => {
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const logoColor = useColorModeValue('blue.600', 'blue.200');

  // Redirect if already logged in
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Flex 
      minH="100vh"
      align="center"
      justify="center"
      bg={bgColor}
      direction={{ base: 'column', md: 'row' }}
    >
      {/* Left side with background image and logo */}
      <Box 
        w={{ base: '100%', md: '50%' }}
        h={{ base: '30vh', md: '100vh' }}
        bg="blue.700"
        position="relative"
        display="flex"
        alignItems="center"
        justifyContent="center"
        flexDirection="column"
        padding={8}
        color="white"
      >
        <Box 
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bgImage="url('/assets/images/defense-background.jpg')"
          bgSize="cover"
          bgPosition="center"
          opacity={0.2}
        />
        <Box zIndex={1} textAlign="center">
          <Heading as="h1" size="2xl" mb={4}>SentinelMine</Heading>
          <Text fontSize="xl" fontWeight="medium">
            Predictive Analysis for National Security Operations
          </Text>
          <Text mt={6} fontSize="md" opacity={0.8}>
            Advanced AI-powered platform with real-time threat detection, blockchain verification, and secure intelligence analysis
          </Text>
        </Box>
      </Box>

      {/* Right side with login form */}
      <Flex 
        w={{ base: '100%', md: '50%' }}
        h={{ base: 'auto', md: '100vh' }}
        align="center"
        justify="center"
        p={8}
      >
        <Box maxW="md" width="100%">
          <Box mb={8} textAlign={{ base: 'center', md: 'left' }}>
            <Heading as="h2" size="lg" color="blue.700" mb={2}>
              Secure Authentication
            </Heading>
            <Text color="gray.600">
              Please authenticate to access classified information.
            </Text>
          </Box>
          <LoginForm />
          <Text mt={4} fontSize="sm" color="gray.500" textAlign="center">
            This system is monitored and for authorized use only.
          </Text>
        </Box>
      </Flex>
    </Flex>
  );
};

export default LoginPage; 