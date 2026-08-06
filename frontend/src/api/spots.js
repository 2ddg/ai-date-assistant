import request from './index.js'

export function aiRecommendSpots(payload) {
  return request.post('/spots/ai-recommend', payload)
}

export function getMapView(payload) {
  return request.post('/spots/map-view', payload)
}

export function listPersonas() {
  return request.get('/personas')
}

