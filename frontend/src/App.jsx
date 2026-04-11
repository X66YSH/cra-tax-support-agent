import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { createSession, listSessions, getSession, deleteSession, sendMessage } from './api';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState(null);
  const [dark, setDark] = useState(() => window.matchMedia('(prefers-color-scheme: dark)').matches);

  // Apply dark class to html
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
  }, [dark]);

  // Load sessions on mount
  useEffect(() => {
    listSessions().then(setSessions);
  }, []);

  // Load messages when active session changes
  useEffect(() => {
    if (!activeId) {
      setMessages([]);
      return;
    }
    getSession(activeId).then((s) => {
      if (s && s.messages) setMessages(s.messages);
    });
  }, [activeId]);

  const handleCreate = useCallback(async () => {
    const s = await createSession();
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
    setMessages([]);
    setActiveAction(null);
  }, []);

  const handleDelete = useCallback(async (id) => {
    await deleteSession(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (activeId === id) {
      setActiveId(null);
      setMessages([]);
    }
  }, [activeId]);

  const handleSend = useCallback(async (text) => {
    let sessionId = activeId;

    // Auto-create session if none active
    if (!sessionId) {
      const s = await createSession();
      setSessions((prev) => [s, ...prev]);
      setActiveId(s.id);
      sessionId = s.id;
    }

    // Optimistic: add user message
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await sendMessage(sessionId, text);

      // Add assistant response
      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        sources: data.sources ? JSON.stringify(data.sources) : null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Track if agent is mid-action (collecting params)
      setActiveAction(data.state?.action || null);

      // Update session title in sidebar
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, title: text.slice(0, 50) + (text.length > 50 ? '...' : ''), updated_at: new Date().toISOString() }
            : s
        )
      );
    } catch (err) {
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }, [activeId]);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={setActiveId}
        onCreate={handleCreate}
        onDelete={handleDelete}
        dark={dark}
        onToggleDark={() => setDark((d) => !d)}
      />
      <ChatWindow
        messages={messages}
        loading={loading}
        onSend={handleSend}
        dark={dark}
        activeAction={activeAction}
      />
    </div>
  );
}
