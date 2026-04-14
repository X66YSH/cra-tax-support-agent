import { useRef, useEffect, useState } from 'react';
import { Landmark, Menu, ChevronDown } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import WelcomeScreen from './WelcomeScreen';
import ChatInput from './ChatInput';
import TaxCalculator from './TaxCalculator';
import ReminderSetup from './ReminderSetup';
import BookClinic from './BookClinic';

const INTERACTIVE_COMPONENTS = {
  tax_estimate: TaxCalculator,
  filing_reminder: ReminderSetup,
  book_appointment: BookClinic,
};

export default function ChatWindow({ messages, loading, onSend, dark, activeAction, onOpenSidebar }) {
  const bottomRef = useRef(null);
  const scrollRef = useRef(null);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [newestMsgId, setNewestMsgId] = useState(null);

  // Track newest message for typewriter effect
  useEffect(() => {
    if (messages.length > 0) {
      const last = messages[messages.length - 1];
      if (last.role === 'assistant') {
        setNewestMsgId(last.id);
      }
    }
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    setShowScrollBtn(scrollHeight - scrollTop - clientHeight > 120);
  };

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Dynamic page title
  useEffect(() => {
    if (messages.length > 0) {
      const firstUserMsg = messages.find((m) => m.role === 'user');
      if (firstUserMsg) {
        const title = firstUserMsg.content.slice(0, 40) + (firstUserMsg.content.length > 40 ? '...' : '');
        document.title = `${title} — CRA Tax Support`;
      }
    } else {
      document.title = 'CRA Tax Support Agent';
    }
  }, [messages]);

  return (
    <div className={`flex-1 flex flex-col h-screen ${dark ? 'bg-chat-bg-dark' : 'bg-chat-bg'}`}>
      {/* Header bar */}
      <div className={`header-blur px-4 md:px-6 py-3 border-b flex items-center gap-3 ${
        dark ? 'border-slate-800' : 'border-slate-200'
      }`}>
        <button
          onClick={onOpenSidebar}
          className={`md:hidden p-1.5 rounded-lg ${dark ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-100'}`}
        >
          <Menu size={18} />
        </button>
        <div className="bot-avatar w-7 h-7 rounded-lg flex items-center justify-center shadow-sm">
          <Landmark size={12} className="text-white" />
        </div>
        <span className={`text-sm font-semibold ${dark ? 'text-slate-200' : 'text-slate-800'}`}>
          CRA Tax Assistant
        </span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          dark ? 'bg-emerald-900/50 text-emerald-400' : 'bg-emerald-50 text-emerald-600'
        }`}>
          Online
        </span>
      </div>

      {/* Messages area */}
      {messages.length === 0 ? (
        <WelcomeScreen onSuggestion={onSend} dark={dark} />
      ) : (
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto px-4 md:px-6 py-4 space-y-4 relative chat-pattern"
        >
          {messages.map((msg) => {
            // Render interactive cards inline
            if (msg.role === 'interactive') {
              const Component = INTERACTIVE_COMPONENTS[msg.interactiveType];
              if (!Component) return null;
              return (
                <div key={msg.id} className="flex gap-3 justify-start">
                  <div className="bot-avatar w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                    <Landmark size={14} className="text-white" />
                  </div>
                  <Component dark={dark} />
                </div>
              );
            }
            // Regular messages
            return (
              <MessageBubble
                key={msg.id}
                message={msg}
                dark={dark}
                isNew={msg.id === newestMsgId}
                onRetry={msg.isError ? () => onSend(msg.retryText) : undefined}
              />
            );
          })}
          {loading && <TypingIndicator dark={dark} />}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Scroll to bottom button */}
      {showScrollBtn && (
        <div className="relative">
          <button
            onClick={scrollToBottom}
            className={`absolute -top-12 left-1/2 -translate-x-1/2 p-2 rounded-full shadow-lg transition-all hover:scale-110 ${
              dark ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            <ChevronDown size={18} />
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={onSend} disabled={loading} dark={dark} activeAction={activeAction} />
    </div>
  );
}
