import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

// Color mode config
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

// Custom colors
const colors = {
  brand: {
    50: '#e6f1ff',
    100: '#c2d9f8',
    200: '#9cc2f0',
    300: '#75abe8',
    400: '#4f94e0',
    500: '#357bc7',
    600: '#27609b',
    700: '#194570',
    800: '#0b2b46',
    900: '#00121d',
  },
  security: {
    low: '#48BB78',
    medium: '#ECC94B',
    high: '#ED8936',
    critical: '#E53E3E',
  },
};

// Custom component styles
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'md',
    },
    variants: {
      solid: (props: any) => ({
        bg: props.colorMode === 'dark' ? 'brand.600' : 'brand.500',
        color: 'white',
        _hover: {
          bg: props.colorMode === 'dark' ? 'brand.500' : 'brand.600',
        },
      }),
      outline: (props: any) => ({
        borderColor: props.colorMode === 'dark' ? 'brand.500' : 'brand.600',
      }),
    },
  },
  Card: {
    baseStyle: (props: any) => ({
      container: {
        bg: props.colorMode === 'dark' ? 'gray.800' : 'white',
        boxShadow: 'md',
        borderRadius: 'md',
      },
    }),
  },
  Heading: {
    baseStyle: {
      fontWeight: 'semibold',
    },
  },
};

// Custom global styles
const styles = {
  global: (props: any) => ({
    body: {
      bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
    },
  }),
};

// Fonts
const fonts = {
  heading: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
  body: `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"`,
};

// Create and export the theme
const theme = extendTheme({
  config,
  colors,
  components,
  styles,
  fonts,
});

export default theme; 