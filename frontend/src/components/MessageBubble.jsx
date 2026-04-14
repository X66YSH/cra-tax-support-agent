import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Landmark, Copy, Check, RotateCcw, FileText, ThumbsUp, ThumbsDown } from 'lucide-react';
import SourcePreview from './SourcePreview';
import { formatRelative } from '../utils/time';
import { useToast } from './Toast';

// Custom link renderer — opens in new tab with proper styling
const markdownComponents = {
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-indigo-500 dark:text-indigo-400 underline hover:text-indigo-700 dark:hover:text-indigo-300"
    >
      {children}
    </a>
  ),
};

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
      <ReactMarkdown components={markdownComponents}>{displayed}</ReactMarkdown>
      {!done && <span className="typing-cursor" />}
    </div>
  );
}

export default function MessageBubble({ message, dark, isNew, onRetry }) {
  const isUser = message.role === 'user';
  const isError = message.isError;
  const [copied, setCopied] = useState(false);
  const [activeSource, setActiveSource] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [reaction, setReaction] = useState(null); // 'up' | 'down' | null
  const [tick, setTick] = useState(0); // force re-render for relative time
  const bubbleRef = useRef(null);
  const sources = message.sources ? JSON.parse(message.sources) : null;
  const { show: showToast } = useToast();

  // Update relative timestamps every minute
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 60000);
    return () => clearInterval(interval);
  }, []);

  const handleReaction = (type) => {
    const newReaction = reaction === type ? null : type;
    setReaction(newReaction);
    if (newReaction === 'up') showToast('Thanks for the feedback!', 'success', 1800);
    if (newReaction === 'down') showToast('Thanks — we\'ll improve this.', 'info', 1800);
  };

  // Scroll reveal — trigger when bubble enters viewport
  useEffect(() => {
    const el = bubbleRef.current;
    if (!el) return;
    // For newly created messages, reveal immediately
    if (isNew) {
      setRevealed(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setRevealed(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [isNew]);

  // Strip [Source N] references from displayed text since we show them as labels below
  const cleanContent = message.content
    ? message.content.replace(/\[Source\s*\d+\]/gi, '').replace(/\n{3,}/g, '\n\n').trim()
    : '';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    showToast('Copied to clipboard', 'success', 1500);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      ref={bubbleRef}
      className={`msg-enter scroll-reveal group ${revealed ? 'revealed' : ''} flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <img src="/logo.svg" alt="CRA Tax" className="w-8 h-8 rounded-full flex-shrink-0 mt-1 shadow-sm" />
      )}

      <div className={`max-w-[85%] md:max-w-[70%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`group relative px-4 py-3 rounded-2xl text-sm leading-relaxed bubble-3d ${
            isUser
              ? 'user-bubble user-bubble-3d text-white rounded-br-md'
              : isError
                ? dark
                  ? 'bg-red-900/30 border border-red-800/50 text-red-300 rounded-bl-md'
                  : 'bg-red-50 border border-red-200 text-red-700 rounded-bl-md'
                : dark
                  ? 'glass-bubble bot-bubble-3d text-slate-200 rounded-bl-md'
                  : 'glass-bubble bot-bubble-3d text-slate-800 rounded-bl-md'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : isNew && !isError ? (
            <TypewriterText content={cleanContent} dark={dark} />
          ) : (
            <div className="message-content">
              <ReactMarkdown components={markdownComponents}>{cleanContent}</ReactMarkdown>
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

        {/* Sources — click to open preview sheet */}
        {!isUser && sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {sources.map((src, i) => (
              <button
                key={i}
                onClick={() => setActiveSource(src)}
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium transition-all hover:scale-105 ${
                  dark
                    ? 'bg-slate-700/80 text-blue-400 hover:bg-slate-600'
                    : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                }`}
                title={`${src.title} — click to preview`}
              >
                <FileText size={10} />
                Source {i + 1}
              </button>
            ))}
          </div>
        )}

        {/* Source preview sheet */}
        {activeSource && (
          <SourcePreview
            source={activeSource}
            onClose={() => setActiveSource(null)}
            dark={dark}
          />
        )}

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

        <div className={`flex items-center gap-2 mt-1 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <p className={`text-[10px] ${dark ? 'text-slate-600' : 'text-slate-400'}`}>
            {message.created_at ? formatRelative(message.created_at) : ''}
          </p>
          {!isUser && !isError && (
            <div className="flex items-center gap-0.5">
              <button
                onClick={() => handleReaction('up')}
                className={`p-1 rounded-md transition-all opacity-0 group-hover:opacity-100 hover:scale-110 ${
                  reaction === 'up'
                    ? 'opacity-100 text-emerald-500'
                    : dark ? 'text-slate-500 hover:text-emerald-400' : 'text-slate-400 hover:text-emerald-500'
                }`}
                title="Good response"
              >
                <ThumbsUp size={11} fill={reaction === 'up' ? 'currentColor' : 'none'} />
              </button>
              <button
                onClick={() => handleReaction('down')}
                className={`p-1 rounded-md transition-all opacity-0 group-hover:opacity-100 hover:scale-110 ${
                  reaction === 'down'
                    ? 'opacity-100 text-red-500'
                    : dark ? 'text-slate-500 hover:text-red-400' : 'text-slate-400 hover:text-red-500'
                }`}
                title="Bad response"
              >
                <ThumbsDown size={11} fill={reaction === 'down' ? 'currentColor' : 'none'} />
              </button>
            </div>
          )}
        </div>
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
