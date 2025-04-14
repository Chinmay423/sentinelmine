import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Flex,
  useColorModeValue,
  Drawer,
  DrawerContent,
  useDisclosure,
} from '@chakra-ui/react';

// Components
import Sidebar from './Sidebar';
import Navbar from './Navbar';

const Layout: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box minH="100vh" bg={bg}>
      {/* Desktop sidebar */}
      <Sidebar
        display={{ base: 'none', md: 'block' }}
        onClose={() => onClose}
      />

      {/* Mobile sidebar */}
      <Drawer
        autoFocus={false}
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="xs"
      >
        <DrawerContent>
          <Sidebar onClose={onClose} />
        </DrawerContent>
      </Drawer>

      <Box ml={{ base: 0, md: 60 }} transition=".3s ease">
        {/* Top Navigation Bar */}
        <Navbar onMenuButtonClick={onOpen} />

        {/* Main Content */}
        <Box as="main" p={4}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout; 