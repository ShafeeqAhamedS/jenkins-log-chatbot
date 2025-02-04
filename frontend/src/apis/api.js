import axios from 'axios';

const BASE_URL = "http://54.91.213.21"

export const getChats = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/chat`);
        return response.data;
    } catch (error) {
        console.error("Error fetching history:", error);
        throw new Error("Failed to fetch build history. Please try again later.");
    }
};

export const getChatHistory = async (uniqueKey) => {
    try {
        const response = await axios.get(`${BASE_URL}/history/${uniqueKey}`);
        if (response.data.status_code === 404) {
            throw new Error("Chat history not found.");
        }
        return response.data.history;
    } catch (error) {
        console.error("Error fetching chat history:", error);
        throw new Error("Failed to fetch chat history. Please try again later.");
    }
}

export const sendMessage = async (prompt) => {
    try {
        const response = await axios.post(`${BASE_URL}/chatbot`, { prompt });
        return response.data;
    } catch (error) {
        console.error("Error sending message:", error);
        throw new Error("Failed to send message. Please try again later.");
    }
};

export const sendMessagetoSpecificChat = async (uniqueKey, prompt) => {
    try {
        const response = await axios.post(`${BASE_URL}/chatbot/${uniqueKey}`, { prompt });
        return response.data;
    } catch (error) {
        console.error("Error sending message:", error);
        throw new Error("Failed to send message. Please try again later.");
    }
};

export const getSpecificLog = async (uniqueKey) => {
    try {
        const response = await axios.get(`${BASE_URL}/chatbot/${uniqueKey}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching specific log:", error);
        throw new Error("Failed to fetch specific log. Please try again later.");
    }
};

export const searchLogs = async (keyword) => {
    try {
        const response = await axios.get(`${BASE_URL}/search?keyword=${keyword}`);
        return response.data.results;
    } catch (error) {
        console.error("Error searching logs:", error);
        throw new Error("Failed to search logs. Please try again later.");
    }
}
