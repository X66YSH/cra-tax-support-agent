import { useRef, useEffect } from 'react';
import { Landmark } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import WelcomeScreen from './WelcomeScreen';
import ChatInput from './ChatInput';

export default function ChatWindow({ messages, loading, onSend, dark, activeAction }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className={`flex-1 flex flex-col h-screen ${dark ? 'bg-chat-bg-dark' : 'bg-chat-bg'}`}>
      {/* Header bar */}
      <div className={`header-blur px-6 py-3 border-b flex items-center gap-3 ${
        dark ? 'border-slate-800' : 'border-slate-200'
      }`}>
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
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} dark={dark} />
          ))}
          {loading && <TypingIndicator dark={dark} />}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={onSend} disabled={loading} dark={dark} activeAction={activeAction} />
    </div>
  );
}
