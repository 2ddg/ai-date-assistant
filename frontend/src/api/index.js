import axios from 'axios'
import config from '../config.js'
import { useUserStore } from '../stores/user.js'

const request = axios.create({
  baseURL: config.apiBase,
  timeout: config.timeout,
})

request.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const store = useUserStore()
      store.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
