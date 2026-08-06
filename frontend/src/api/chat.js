import request from './index.js'

export function sendMessage(personaId, message) {
  return request.post('/chat/send', { persona_id: personaId, message })
}

export function getHistory(personaId) {
  return request.get(`/chat/history/${personaId}`)
}

export function streamChat(personaId, message) {
  const token = localStorage.getItem('token')
  return fetch(`/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ persona_id: personaId, message }),
  })
}
