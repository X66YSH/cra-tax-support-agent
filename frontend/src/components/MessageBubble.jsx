import ReactMarkdown from 'react-markdown';
import { User, Landmark, ExternalLink } from 'lucide-react';

export default function MessageBubble({ message, dark }) {
  const isUser = message.role === 'user';
  const sources = message.sources ? JSON.parse(message.sources) : null;

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="bot-avatar w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <Landmark size={14} className="text-white" />
        </div>
      )}

      <div className={`max-w-[70%] ${isUser ? 'order-first' : ''}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'user-bubble text-white rounded-br-md shadow-md'
              : dark
                ? 'glass-bubble text-slate-200 rounded-bl-md'
                : 'glass-bubble text-slate-800 rounded-bl-md shadow-sm'
          }`}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {sources && sources.length > 0 && (
          <div className="mt-2 px-1">
            <p className={`text-xs font-medium mb-1 ${dark ? 'text-slate-500' : 'text-slate-400'}`}>
              Sources
            </p>
            <div className="flex flex-wrap gap-1.5">
              {sources.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs transition-colors ${
                    dark
                      ? 'bg-slate-700 text-indigo-400 hover:bg-slate-600'
                      : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
                  }`}
                >
                  <ExternalLink size={10} />
                  <span className="truncate max-w-[180px]">{src.title}</span>
                </a>
              ))}
            </div>
          </div>
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
