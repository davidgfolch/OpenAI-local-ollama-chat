import axios from 'axios';

const server = 'http://127.0.0.1:5000';
// Create an Axios instance
const apiClient = axios.create({
  baseURL: server,
})
apiClient.interceptors.response.use((response) => response, (error) => {
  if (error=='AxiosError: Network Error')
    throw new Error("Could not connect to backend server: " + server);
  throw error;
});
export default apiClient;