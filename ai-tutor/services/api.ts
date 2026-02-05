import axios from 'axios';
import { Platform } from 'react-native';

// Use your computer's LAN IP so real devices can connect.
// REPLACE_THIS_WITH_YOUR_IP: 192.168.1.XX
const BASE_URL = 'http://192.168.31.39:8000';


const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const checkHealth = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error("Health Check Failed:", error);
        return null;
    }
};

export const chatWithAI = async (question: string) => {
    try {
        const response = await api.post('/chat', { question });
        return response.data;
    } catch (error) {
        console.error("Chat Error:", error);
        throw error;
    }
};

export default api;
