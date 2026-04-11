import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Landmark, Copy, Check, RotateCcw } from 'lucide-react';

function TypewriterText({ content, dark }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  const idx = useRef(0);

  useEffect(() => {
    // Skip typewriter for short messages or previously loaded messages
    if (content.length < 20) {
      setDisplayed(content);
      setDone(true);
      return;
    }

    idx.current = 0;
    setDisplayed('');
    setDone(false);

    const speed = Math.max(8, Math.min(20, 2000 / content.length));
    const timer = setInterval(() => {
      idx.current += 2;
      if (idx.current >= content.length) {
        setDisplayed(content);
        setDone(true);
        clearInterval(timer);
      } else {
        setDisplayed(content.slice(0, idx.current));
      }
    }, speed);

    return () => clearInterval(timer);
  }, [content]);

  return (
    <div className="message-content">
      <ReactMarkdown>{displayed}</ReactMarkdown>
      {!done && <span className="typing-cursor" />}
    </div>
  );
}

export default function MessageBubble({ message, dark, isNew, onRetry }) {
  const isUser = message.role === 'user';
  const isError = message.isError;
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`msg-enter flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="bot-avatar w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <Landmark size={14} className="text-white" />
        </div>
      )}

      <div className={`max-w-[85%] md:max-w-[70%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`group relative px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'user-bubble text-white rounded-br-md shadow-md'
              : isError
                ? dark
                  ? 'bg-red-900/30 border border-red-800/50 text-red-300 rounded-bl-md'
                  : 'bg-red-50 border border-red-200 text-red-700 rounded-bl-md'
                : dark
                  ? 'glass-bubble text-slate-200 rounded-bl-md'
                  : 'glass-bubble text-slate-800 rounded-bl-md shadow-sm'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : isNew && !isError ? (
            <TypewriterText content={message.content} dark={dark} />
          ) : (
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}

          {/* Copy button for bot messages */}
          {!isUser && !isError && (
            <button
              onClick={handleCopy}
              className={`absolute -bottom-3 right-2 p-1 rounded-md text-xs opacity-0 group-hover:opacity-100 transition-opacity ${
                dark ? 'bg-slate-700 text-slate-400 hover:text-slate-200' : 'bg-slate-100 text-slate-400 hover:text-slate-600'
              }`}
              title="Copy message"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
            </button>
          )}
        </div>

        {/* Retry button for errors */}
        {isError && onRetry && (
          <button
            onClick={onRetry}
            className={`mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              dark
                ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <RotateCcw size={12} />
            Retry
          </button>
        )}

        <p className={`text-[10px] mt-1 px-1 ${
          isUser ? 'text-right' : 'text-left'
        } ${dark ? 'text-slate-600' : 'text-slate-400'}`}>
          {message.created_at
            ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : ''}
        </p>
      </div>

      {isUser && (
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm ${
          dark ? 'bg-slate-600' : 'bg-slate-200'
        }`}>
          <User size={14} className={dark ? 'text-slate-300' : 'text-slate-600'} />
        </div>
      )}
    </div>
  );
}
