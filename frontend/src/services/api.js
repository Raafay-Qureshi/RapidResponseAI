import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5001/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Disaster API endpoints
export const disasterAPI = {
  /**
   * Trigger a new disaster simulation
   * @param {Object} disasterData - { type, location, severity }
   * @returns {Promise} Response with disaster_id
   */
  trigger: async (disasterData) => {
    try {
      const response = await api.post('/disaster/trigger', disasterData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to trigger disaster: ${error.message}`);
    }
  },

  /**
   * Get disaster status and data
   * @param {string} disasterId - Disaster ID
   * @returns {Promise} Disaster object
   */
  getDisaster: async (disasterId) => {
    try {
      const response = await api.get(`/disaster/${disasterId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch disaster: ${error.message}`);
    }
  },

  /**
   * Get generated emergency plan
   * @param {string} disasterId - Disaster ID
   * @returns {Promise} Plan object
   */
  getPlan: async (disasterId) => {
    try {
      const response = await api.get(`/disaster/${disasterId}/plan`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch plan: ${error.message}`);
    }
  },

  /**
   * Test backend connectivity
   * @returns {Promise} Status object
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`Backend not reachable: ${error.message}`);
    }
  },
};

export default api;