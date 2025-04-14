import React from 'react';
import {
  Box,
  Flex,
  Text,
  IconButton,
  Button,
  Stack,
  Collapse,
  Icon,
  Popover,
  PopoverTrigger,
  PopoverContent,
  useColorModeValue,
  useBreakpointValue,
  useDisclosure,
  HStack,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Badge,
  InputGroup,
  Input,
  InputRightElement,
  useColorMode,
} from '@chakra-ui/react';
import {
  HamburgerIcon,
  CloseIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  SearchIcon,
  BellIcon,
  MoonIcon,
  SunIcon,
} from '@chakra-ui/icons';
import { FiLogOut, FiUser, FiSettings } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';

interface NavbarProps {
  onMenuButtonClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuButtonClick }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  // Mock user data - would come from Redux store in a real app
  const user = {
    name: 'John Analyst',
    role: 'Intelligence Analyst',
    avatarUrl: 'https://i.pravatar.cc/300',
  };
  
  // Function to handle logout
  const handleLogout = () => {
    // In a real app, you would dispatch a logout action
    // dispatch({ type: 'auth/logout' });
    navigate('/login');
  };
  
  return (
    <Box
      as="header"
      position="sticky"
      top="0"
      zIndex="1"
      bg={useColorModeValue('white', 'gray.800')}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
      shadow="sm"
    >
      <Flex
        px={{ base: 4, md: 6 }}
        py={4}
        align="center"
        justify="space-between"
      >
        {/* Left side: Mobile menu button and search */}
        <HStack spacing={4}>
          <IconButton
            display={{ base: 'flex', md: 'none' }}
            onClick={onMenuButtonClick}
            variant="ghost"
            aria-label="open menu"
            icon={<HamburgerIcon />}
          />
          
          <Text
            display={{ base: 'flex', md: 'none' }}
            fontSize="lg"
            fontWeight="bold"
          >
            SentinelMine
          </Text>
          
          <InputGroup maxW={{ base: '12rem', md: '20rem' }} display={{ base: 'none', md: 'flex' }}>
            <Input
              placeholder="Search..."
              variant="filled"
              bg={useColorModeValue('gray.100', 'gray.700')}
              _focus={{
                bg: useColorModeValue('gray.200', 'gray.600'),
              }}
              size="sm"
            />
            <InputRightElement pointerEvents="none" children={<SearchIcon color="gray.400" />} />
          </InputGroup>
        </HStack>
        
        {/* Right side: Notifications, theme toggle, and profile */}
        <HStack spacing={3}>
          {/* Notifications */}
          <Menu>
            <MenuButton
              as={IconButton}
              variant="ghost"
              aria-label="Notifications"
              icon={
                <>
                  <BellIcon />
                  <Badge
                    position="absolute"
                    top="0"
                    right="0"
                    transform="translate(40%, -30%)"
                    borderRadius="full"
                    variant="solid"
                    colorScheme="red"
                    size="xs"
                  >
                    3
                  </Badge>
                </>
              }
            />
            <MenuList>
              <MenuItem>New prediction alert</MenuItem>
              <MenuItem>System update notification</MenuItem>
              <MenuItem>Security alert detected</MenuItem>
              <MenuDivider />
              <MenuItem>View all notifications</MenuItem>
            </MenuList>
          </Menu>
          
          {/* Theme toggle */}
          <IconButton
            aria-label="Toggle theme"
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            variant="ghost"
            onClick={toggleColorMode}
          />
          
          {/* User profile */}
          <Menu>
            <MenuButton as={Button} variant="ghost" rightIcon={<ChevronDownIcon />} px={2}>
              <HStack spacing={2}>
                <Avatar size="sm" src={user.avatarUrl} />
                <Box display={{ base: 'none', md: 'block' }}>
                  <Text fontSize="sm" fontWeight="medium">{user.name}</Text>
                  <Text fontSize="xs" color="gray.500">{user.role}</Text>
                </Box>
              </HStack>
            </MenuButton>
            <MenuList>
              <MenuItem icon={<FiUser />} onClick={() => navigate('/profile')}>
                Profile
              </MenuItem>
              <MenuItem icon={<FiSettings />} onClick={() => navigate('/settings')}>
                Settings
              </MenuItem>
              <MenuDivider />
              <MenuItem icon={<FiLogOut />} onClick={handleLogout}>
                Sign Out
              </MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar; 