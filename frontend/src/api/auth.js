import request from './index.js'

export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

export function register(username, password, nickname) {
  return request.post('/auth/register', { username, password, nickname })
}
