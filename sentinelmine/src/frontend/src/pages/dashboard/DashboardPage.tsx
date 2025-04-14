import React, { useState } from 'react';
import {
  Box,
  Flex,
  Grid,
  GridItem,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  IconButton,
  Select,
  HStack,
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiAlertTriangle, FiShield, FiTrendingUp, FiEye, FiRefreshCw } from 'react-icons/fi';

// Sample components - in a real app, these would be in separate files
import ThreatMap from '../../components/dashboard/ThreatMap';
import ActivityTimeline from '../../components/dashboard/ActivityTimeline';
import PredictionsSummary from '../../components/dashboard/PredictionsSummary';
import ThreatLevelChart from '../../components/dashboard/ThreatLevelChart';

// For demo, we'll mock these components with placeholder content
const MockThreatMap = () => (
  <Box 
    bg={useColorModeValue('gray.200', 'gray.700')} 
    h="100%" 
    minH="250px" 
    borderRadius="md" 
    p={4}
    display="flex"
    alignItems="center"
    justifyContent="center"
  >
    <Text textAlign="center" fontWeight="medium">World Threat Map</Text>
  </Box>
);

const MockActivityTimeline = () => (
  <Box
    bg={useColorModeValue('white', 'gray.800')}
    h="100%"
    borderRadius="md"
    boxShadow="sm"
    p={4}
    overflowY="auto"
  >
    <Text fontWeight="medium" mb={4}>Recent Activity</Text>
    {[1, 2, 3, 4, 5].map((i) => (
      <Box 
        key={i} 
        p={3} 
        mb={3} 
        borderRadius="md" 
        borderLeft="4px solid"
        borderLeftColor={i % 3 === 0 ? 'red.500' : i % 2 === 0 ? 'yellow.500' : 'blue.500'}
        bg={useColorModeValue('gray.50', 'gray.700')}
      >
        <Flex justify="space-between" align="center">
          <Text fontSize="sm" fontWeight="medium">
            {i % 3 === 0 ? 'Critical Alert' : i % 2 === 0 ? 'Prediction Completed' : 'New Intelligence'}
          </Text>
          <Badge size="sm" colorScheme={i % 3 === 0 ? 'red' : i % 2 === 0 ? 'yellow' : 'blue'}>
            {i % 3 === 0 ? 'High' : i % 2 === 0 ? 'Medium' : 'Info'}
          </Badge>
        </Flex>
        <Text fontSize="xs" color="gray.500" mt={1}>10 minutes ago</Text>
      </Box>
    ))}
  </Box>
);

const MockThreatLevelChart = () => (
  <Box 
    bg={useColorModeValue('white', 'gray.800')}
    h="100%"
    borderRadius="md"
    boxShadow="sm"
    p={4}
  >
    <Text fontWeight="medium" mb={4}>Threat Level Trends</Text>
    <Box 
      h="150px" 
      bg={useColorModeValue('gray.100', 'gray.700')} 
      borderRadius="md" 
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Text fontSize="sm">Chart Visualization</Text>
    </Box>
  </Box>
);

const DashboardPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  
  // Color values
  const cardBg = useColorModeValue('white', 'gray.800');
  const statCardBg = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  return (
    <Box>
      {/* Header */}
      <Flex 
        justify="space-between" 
        align="center" 
        mb={6}
        flexDir={{ base: 'column', md: 'row' }}
        gap={4}
      >
        <Box>
          <Heading size="lg" mb={1}>Intelligence Dashboard</Heading>
          <Text color="gray.500">Real-time security operations overview</Text>
        </Box>
        
        <HStack spacing={4}>
          <Select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            size="sm"
            w="120px"
          >
            <option value="6h">Last 6 hours</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </Select>
          
          <Button 
            leftIcon={<FiRefreshCw />} 
            size="sm" 
            colorScheme="blue" 
            variant="outline"
          >
            Refresh
          </Button>
        </HStack>
      </Flex>
      
      {/* Key metrics */}
      <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={4} mb={6}>
        <Stat
          bg={statCardBg}
          p={4}
          borderRadius="md"
          boxShadow="sm"
        >
          <StatLabel>Active Threats</StatLabel>
          <Flex align="center">
            <FiAlertTriangle color="red" />
            <StatNumber ml={2}>12</StatNumber>
          </Flex>
          <StatHelpText>
            <StatArrow type="increase" />
            23% increase
          </StatHelpText>
        </Stat>
        
        <Stat
          bg={cardBg}
          p={4}
          borderRadius="md"
          boxShadow="sm"
        >
          <StatLabel>Security Score</StatLabel>
          <Flex align="center">
            <FiShield color="green" />
            <StatNumber ml={2}>78%</StatNumber>
          </Flex>
          <StatHelpText>
            <StatArrow type="decrease" />
            5% decrease
          </StatHelpText>
        </Stat>
        
        <Stat
          bg={cardBg}
          p={4}
          borderRadius="md"
          boxShadow="sm"
        >
          <StatLabel>Predictions</StatLabel>
          <Flex align="center">
            <FiTrendingUp color="blue" />
            <StatNumber ml={2}>54</StatNumber>
          </Flex>
          <StatHelpText>
            <StatArrow type="increase" />
            12 new today
          </StatHelpText>
        </Stat>
        
        <Stat
          bg={cardBg}
          p={4}
          borderRadius="md"
          boxShadow="sm"
        >
          <StatLabel>Systems Monitored</StatLabel>
          <Flex align="center">
            <FiEye color="purple" />
            <StatNumber ml={2}>143</StatNumber>
          </Flex>
          <StatHelpText>
            <Badge colorScheme="green">All Normal</Badge>
          </StatHelpText>
        </Stat>
      </SimpleGrid>
      
      {/* Main content */}
      <Grid
        templateColumns={{ base: 'repeat(1, 1fr)', lg: 'repeat(3, 1fr)' }}
        templateRows={{ base: 'auto', lg: 'repeat(2, 1fr)' }}
        gap={6}
      >
        {/* Threat Map - spans 2 columns */}
        <GridItem colSpan={{ base: 1, lg: 2 }} rowSpan={1}>
          <Card bg={cardBg}>
            <CardHeader pb={0}>
              <Flex justify="space-between" align="center">
                <Heading size="md">Global Threat Map</Heading>
                <IconButton
                  aria-label="Refresh map"
                  icon={<FiRefreshCw />}
                  size="sm"
                  variant="ghost"
                />
              </Flex>
            </CardHeader>
            <CardBody>
              <MockThreatMap />
            </CardBody>
          </Card>
        </GridItem>
        
        {/* Activity timeline */}
        <GridItem colSpan={1} rowSpan={2}>
          <MockActivityTimeline />
        </GridItem>
        
        {/* Charts - second row */}
        <GridItem colSpan={{ base: 1, lg: 2 }} rowSpan={1}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            <MockThreatLevelChart />
            
            <Card bg={cardBg}>
              <CardHeader pb={0}>
                <Heading size="md">Prediction Accuracy</Heading>
              </CardHeader>
              <CardBody>
                <Box
                  h="150px" 
                  bg={useColorModeValue('gray.100', 'gray.700')} 
                  borderRadius="md" 
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text fontSize="sm">Accuracy Chart</Text>
                </Box>
              </CardBody>
            </Card>
          </SimpleGrid>
        </GridItem>
      </Grid>
    </Box>
  );
};

export default DashboardPage; 