import request from './index.js'

export function uploadImage(file) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/outfit/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function analyzeOutfit(imageId, occasion = '') {
  return request.post('/outfit/analyze', null, {
    params: { image_id: imageId, occasion },
  })
}

export function listImages() {
  return request.get('/outfit/list')
}

export function getImageDetail(imageId) {
  return request.get(`/outfit/${imageId}`)
}
