import axios from 'axios';

// Types
export interface PredictionRequest {
  prediction_type: string;
  input_data: Record<string, any>;
  source_systems?: string[];
  priority?: number;
  tags?: string[];
  context?: Record<string, any>;
}

export interface Prediction {
  id: string;
  prediction_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  result?: Record<string, any>;
  confidence_score?: number;
  processing_time_ms?: number;
  source_systems: string[];
  tags: string[];
  priority: number;
  blockchain_verification?: Record<string, any>;
}

export interface PredictionListResponse {
  predictions: Prediction[];
  total: number;
  page: number;
  page_size: number;
}

export interface PredictionVerificationResponse {
  verified: boolean;
  blockchain_reference: string;
  verification_time: string;
  verifier: string;
}

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Service methods
const predictionService = {
  // Get predictions list
  getPredictions: async (
    page: number = 1,
    pageSize: number = 10,
    status?: string,
    predictionType?: string
  ): Promise<PredictionListResponse> => {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());
      
      if (status) {
        params.append('status', status);
      }
      
      if (predictionType) {
        params.append('prediction_type', predictionType);
      }
      
      const response = await api.get(`/predictions?${params.toString()}`);
      return response.data;
    } catch (error) {
      // In a real app, you would handle errors better
      console.error('Error fetching predictions:', error);
      throw error;
    }
  },

  // Get prediction by ID
  getPredictionById: async (id: string): Promise<Prediction> => {
    try {
      const response = await api.get(`/predictions/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching prediction ${id}:`, error);
      throw error;
    }
  },

  // Create new prediction
  createPrediction: async (data: PredictionRequest): Promise<Prediction> => {
    try {
      const response = await api.post('/predictions', data);
      return response.data;
    } catch (error) {
      console.error('Error creating prediction:', error);
      throw error;
    }
  },

  // Verify prediction
  verifyPrediction: async (id: string): Promise<PredictionVerificationResponse> => {
    try {
      const response = await api.post(`/predictions/${id}/verify`);
      return response.data;
    } catch (error) {
      console.error(`Error verifying prediction ${id}:`, error);
      throw error;
    }
  },
  
  // Mock data for development
  getMockPredictions: (): Prediction[] => {
    return [
      {
        id: 'pred-001',
        prediction_type: 'threat_assessment',
        status: 'completed',
        created_at: '2023-11-01T14:22:31Z',
        completed_at: '2023-11-01T14:23:45Z',
        result: {
          threat_level: 'medium',
          threat_vectors: ['cyber', 'physical'],
          recommended_actions: [
            'Increase network monitoring',
            'Review access controls'
          ],
          time_sensitivity: '48 hours',
          impacted_assets: ['database-cluster-03', 'api-gateway-north']
        },
        confidence_score: 0.87,
        processing_time_ms: 74200,
        source_systems: ['SIEM', 'ThreatIntel'],
        tags: ['network', 'critical-infrastructure'],
        priority: 2,
        blockchain_verification: {
          transaction_id: 'tx-abc123',
          timestamp: '2023-11-01T14:24:01Z',
          hash: '0x9a8b7c6d5e4f3g2h1i',
          verified: true
        }
      },
      {
        id: 'pred-002',
        prediction_type: 'network_intrusion',
        status: 'completed',
        created_at: '2023-11-02T09:12:55Z',
        completed_at: '2023-11-02T09:14:22Z',
        result: {
          intrusion_detected: true,
          attack_pattern: 'APT29-like',
          source_indicators: ['45.x.x.x', '62.x.x.x'],
          affected_systems: ['auth-server', 'file-storage'],
          data_exfiltration: {
            detected: true,
            volume_estimate: '2.3GB'
          }
        },
        confidence_score: 0.91,
        processing_time_ms: 87340,
        source_systems: ['NetFlow', 'NIDS', 'Firewall'],
        tags: ['apt', 'data-exfiltration', 'advanced-threat'],
        priority: 1,
        blockchain_verification: {
          transaction_id: 'tx-def456',
          timestamp: '2023-11-02T09:15:01Z',
          hash: '0x8h7g6f5e4d3c2b1a',
          verified: true
        }
      },
      {
        id: 'pred-003',
        prediction_type: 'geopolitical_risk',
        status: 'pending',
        created_at: '2023-11-03T11:45:12Z',
        source_systems: ['OSINT', 'IntelFeeds'],
        tags: ['geopolitical', 'strategic'],
        priority: 3
      }
    ];
  }
};

export default predictionService; 