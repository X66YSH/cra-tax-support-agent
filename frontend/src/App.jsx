import { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { createSession, listSessions, getSession, deleteSession, sendMessage } from './api';

const INTERACTIVE_ACTIONS = {
  'tax_estimate': 'Tax Estimate',
  'benefit_eligibility': 'Benefit Check',
  'filing_reminder': 'Filing Reminder',
  'book_appointment': 'Book Clinic',
};

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  // Interactive cards are now stored as special messages in the messages array
  const lastUserMsg = useRef(null);
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('dark-mode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Persist and apply dark class
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('dark-mode', dark);
  }, [dark]);

  // Load sessions on mount
  useEffect(() => {
    listSessions().then((data) => {
      const sorted = [...data].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
      setSessions(sorted);
    });
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
    setSidebarOpen(false);
  }, []);

  const handleDelete = useCallback(async (id) => {
    await deleteSession(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (activeId === id) {
      setActiveId(null);
      setMessages([]);
    }
  }, [activeId]);

  // Check if text matches an interactive action chip
  const getInteractiveAction = (text) => {
    const lower = text.toLowerCase();
    if (lower.includes('estimate my tax') || lower.includes('i want to estimate')) return 'tax_estimate';
    // benefit_eligibility goes through LLM chat, not interactive card
    if (lower.includes('filing reminder') || lower.includes('set up a filing')) return 'filing_reminder';
    if (lower.includes('book a tax clinic') || lower.includes('book clinic') || lower.includes('book appointment')) return 'book_appointment';
    return null;
  };

  const handleSend = useCallback(async (text) => {
    // Check if this should open an interactive card instead
    const interactiveType = getInteractiveAction(text);
    if (interactiveType) {
      // Add a user message
      const userMsg = {
        id: Date.now(),
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Add interactive card as a special message
      const card = {
        id: Date.now() + 1,
        role: 'interactive',
        interactiveType,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, card]);

      // Update session title
      if (activeId) {
        const title = INTERACTIVE_ACTIONS[interactiveType];
        setSessions((prev) => {
          const updated = prev.map((s) =>
            s.id === activeId ? { ...s, title, updated_at: new Date().toISOString() } : s
          );
          return updated.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
        });
      }
      return;
    }

    let sessionId = activeId;
    lastUserMsg.current = text;

    if (!sessionId) {
      const s = await createSession();
      setSessions((prev) => [s, ...prev]);
      setActiveId(s.id);
      sessionId = s.id;
    }

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

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        sources: data.sources ? JSON.stringify(data.sources) : null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      setActiveAction(data.state?.action || null);

      setSessions((prev) => {
        const updated = prev.map((s) =>
          s.id === sessionId
            ? { ...s, title: text.slice(0, 50) + (text.length > 50 ? '...' : ''), updated_at: new Date().toISOString() }
            : s
        );
        return updated.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
      });
    } catch (err) {
      const errMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Something went wrong. Check your connection and try again.',
        created_at: new Date().toISOString(),
        isError: true,
        retryText: text,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }, [activeId]);

  const handleSelect = useCallback((id) => {
    setActiveId(id);
    setSidebarOpen(false);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className={`fixed md:relative z-40 h-screen transition-transform duration-200 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}>
        <Sidebar
          sessions={sessions}
          activeId={activeId}
          onSelect={handleSelect}
          onCreate={handleCreate}
          onDelete={handleDelete}
          dark={dark}
          onToggleDark={() => setDark((d) => !d)}
        />
      </div>

      <ChatWindow
        messages={messages}
        loading={loading}
        onSend={handleSend}
        dark={dark}
        activeAction={activeAction}
        onOpenSidebar={() => setSidebarOpen(true)}
      />
    </div>
  );
}
