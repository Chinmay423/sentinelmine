# SentinelMine Frontend

The frontend web application for SentinelMine - Predictive Analysis for National Security Operations.

## Overview

This React TypeScript application provides a secure interface for intelligence analysts and security professionals to access SentinelMine's predictive analysis capabilities. The application features real-time dashboards, interactive visualizations, and secure access to intelligence data.

## Key Features

- **Secure Authentication**: Multi-factor authentication with role-based access control
- **Real-time Dashboard**: Live monitoring of security intelligence and threat patterns
- **Predictive Analysis Tools**: Access to AI-powered predictive models for threat assessment
- **Blockchain Verification**: Immutable verification of predictions and analysis
- **Interactive Visualizations**: Advanced data visualization for complex intelligence data
- **Dark/Light Mode**: Support for different working environments

## Technology Stack

- React 18 with TypeScript
- Redux Toolkit for state management
- Chakra UI for component library
- React Query for data fetching and caching
- Axios for API communication
- Chart.js and D3.js for visualizations
- Redux Persist for state persistence

## Project Structure

```
src/
├── components/      # Reusable UI components
├── hooks/           # Custom React hooks
├── pages/           # Application pages/routes
├── services/        # API service modules
├── store/           # Redux store configuration and slices
├── utils/           # Utility functions and helpers
├── types/           # TypeScript type definitions
└── App.tsx          # Main application component
```

## Development

### Prerequisites

- Node.js 18+ and npm/yarn
- Access to SentinelMine API services

### Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. Build for production:
   ```
   npm run build
   ```

## Security

This application implements several security measures:

- JWT-based authentication with refresh tokens
- HTTPS-only communication
- Content Security Policy headers
- Secure localStorage handling
- Input sanitization
- Network request encryption

## Integration

The frontend integrates with the following backend services:

- Authentication API
- Predictions API
- Analytics API
- Blockchain Verification API

## Deployment

The application is deployed within a secure Docker container as part of the SentinelMine platform.

## License

Proprietary and Classified - Access Restricted 