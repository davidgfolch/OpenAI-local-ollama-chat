import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:5000',
  });  

const app=createApp(App)
app.config.globalProperties.$apiClient = { ...apiClient }
app.mount('#app')
