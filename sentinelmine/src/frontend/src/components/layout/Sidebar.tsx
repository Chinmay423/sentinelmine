import React from 'react';
import {
  Box,
  Flex,
  Text,
  CloseButton,
  Icon,
  useColorModeValue,
  BoxProps,
  VStack,
  Heading,
  Divider,
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  FiHome,
  FiTrendingUp,
  FiCompass,
  FiStar,
  FiSettings,
  FiAlertCircle,
  FiDatabase,
  FiLock,
  FiUser,
  FiActivity,
} from 'react-icons/fi';
import { IconType } from 'react-icons';

// Define the interface for the navigation items
interface NavItemProps extends BoxProps {
  icon: IconType;
  children: React.ReactNode;
  to: string;
  isActive?: boolean;
}

// Navigation item component
const NavItem = ({ icon, children, to, isActive, ...rest }: NavItemProps) => {
  const activeColor = useColorModeValue('blue.600', 'blue.200');
  const hoverBg = useColorModeValue('blue.50', 'gray.700');
  const activeBg = useColorModeValue('blue.100', 'blue.800');

  return (
    <Box
      as={RouterLink}
      to={to}
      style={{ textDecoration: 'none' }}
      _focus={{ boxShadow: 'none' }}
    >
      <Flex
        align="center"
        p="3"
        mx="2"
        borderRadius="md"
        role="group"
        cursor="pointer"
        bg={isActive ? activeBg : 'transparent'}
        color={isActive ? activeColor : 'inherit'}
        _hover={{
          bg: hoverBg,
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="20"
            _groupHover={{
              color: activeColor,
            }}
            as={icon}
          />
        )}
        {children}
      </Flex>
    </Box>
  );
};

// Navigation items list
const NAV_ITEMS = [
  { name: 'Dashboard', icon: FiHome, path: '/dashboard' },
  { name: 'Predictions', icon: FiTrendingUp, path: '/predictions' },
  { name: 'Alerts', icon: FiAlertCircle, path: '/alerts' },
  { name: 'Analytics', icon: FiActivity, path: '/analytics' },
  { name: 'Settings', icon: FiSettings, path: '/settings' },
];

// Sidebar props
interface SidebarProps extends BoxProps {
  onClose: () => void;
}

// Sidebar component
const Sidebar = ({ onClose, ...rest }: SidebarProps) => {
  const location = useLocation();
  const bg = useColorModeValue('white', 'gray.800');
  
  return (
    <Box
      transition="3s ease"
      bg={bg}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Flex alignItems="center">
          <Box 
            w="8"
            h="8"
            bg="blue.600"
            mr="3"
            borderRadius="md"
            display="flex"
            alignItems="center"
            justifyContent="center"
            color="white"
          >
            <Icon as={FiLock} />
          </Box>
          <Text fontSize="xl" fontWeight="bold">
            SentinelMine
          </Text>
        </Flex>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      
      <Box mt="5">
        <VStack spacing="1" align="stretch">
          <Box px="4" mb="2">
            <Text color="gray.500" fontSize="sm" fontWeight="semibold">
              INTELLIGENCE
            </Text>
          </Box>
          
          {NAV_ITEMS.slice(0, 4).map((item) => (
            <NavItem 
              key={item.name} 
              icon={item.icon} 
              to={item.path}
              isActive={location.pathname === item.path}
            >
              {item.name}
            </NavItem>
          ))}
          
          <Divider my="4" />
          
          <Box px="4" mb="2">
            <Text color="gray.500" fontSize="sm" fontWeight="semibold">
              SYSTEM
            </Text>
          </Box>
          
          {NAV_ITEMS.slice(4).map((item) => (
            <NavItem 
              key={item.name} 
              icon={item.icon} 
              to={item.path}
              isActive={location.pathname === item.path}
            >
              {item.name}
            </NavItem>
          ))}
          
          <NavItem 
            icon={FiUser} 
            to="/profile"
            isActive={location.pathname === '/profile'}
          >
            Profile
          </NavItem>
        </VStack>
      </Box>
      
      <Box position="absolute" bottom="5" width="100%" px="8">
        <Box 
          p="3" 
          bg={useColorModeValue('blue.50', 'gray.700')} 
          borderRadius="md"
          fontSize="sm"
        >
          <Flex align="center" mb="2">
            <Icon as={FiDatabase} mr="2" color="blue.500" />
            <Text fontWeight="medium">Status: Secure</Text>
          </Flex>
          <Text fontSize="xs" color={useColorModeValue('gray.600', 'gray.300')}>
            System operating normally
          </Text>
        </Box>
      </Box>
    </Box>
  );
};

export default Sidebar; 