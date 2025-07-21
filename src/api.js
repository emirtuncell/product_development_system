// api.js
import axios from 'axios'
import router from './router'

const port = window.location.port === "8080" ? "8000" : window.location.port;

const api = axios.create({
  baseURL: `${window.location.protocol}//${window.location.hostname}${port==''?'':':'+port}`,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 401 hatalarını yakala
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      router.push('/login').catch((e)=>{})
    }
    return Promise.reject(error)
  }
)

export default api
