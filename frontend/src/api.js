const API = '/api';

export async function createSession(title = 'New Chat') {
  const res = await fetch(`${API}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  return res.json();
}

export async function listSessions() {
  const res = await fetch(`${API}/sessions`);
  return res.json();
}

export async function getSession(id) {
  const res = await fetch(`${API}/sessions/${id}`);
  return res.json();
}

export async function deleteSession(id) {
  await fetch(`${API}/sessions/${id}`, { method: 'DELETE' });
}

export async function sendMessage(sessionId, message) {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  return res.json();
}

export async function callAction(action, params) {
  const res = await fetch(`${API}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, params }),
  });
  return res.json();
}

export async function createReminder(data) {
  const res = await fetch(`${API}/reminders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}
