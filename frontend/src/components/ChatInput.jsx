import { useState, useRef, useEffect } from 'react';
import { Send, Calculator, Gift, Bell, CalendarCheck } from 'lucide-react';

const actions = [
  { icon: Calculator, label: 'Tax Estimate', message: 'I want to estimate my taxes', color: 'text-blue-400', lightBg: 'bg-blue-50 border-blue-200', darkBg: 'bg-blue-950/30 border-blue-800/50' },
  { icon: Gift, label: 'Benefits', message: 'Check my benefit eligibility', color: 'text-emerald-400', lightBg: 'bg-emerald-50 border-emerald-200', darkBg: 'bg-emerald-950/30 border-emerald-800/50' },
  { icon: Bell, label: 'Filing', message: 'Set up a filing reminder for me', color: 'text-amber-400', lightBg: 'bg-amber-50 border-amber-200', darkBg: 'bg-amber-950/30 border-amber-800/50' },
  { icon: CalendarCheck, label: 'Book Clinic', message: 'I want to book a tax clinic appointment', color: 'text-purple-400', lightBg: 'bg-purple-50 border-purple-200', darkBg: 'bg-purple-950/30 border-purple-800/50' },
];

export default function ChatInput({ onSend, disabled, dark, activeAction }) {
  const [text, setText] = useState('');
  const inputRef = useRef(null);

  // Re-focus input after loading finishes
  useEffect(() => {
    if (!disabled) inputRef.current?.focus();
  }, [disabled]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`border-t px-4 py-3 ${dark ? 'border-slate-800' : 'border-slate-200'}`}>
      {/* Action chips — always visible */}
      <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
        {actions.map((a, i) => (
          <button
            key={i}
            onClick={() => !disabled && onSend(a.message)}
            disabled={disabled}
            className={`action-chip flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border whitespace-nowrap transition-opacity ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            } ${dark ? a.darkBg : a.lightBg} ${a.color}`}
          >
            <a.icon size={13} />
            {a.label}
          </button>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit}>
        <div className={`flex items-end gap-2 rounded-2xl px-4 py-2.5 ${
          dark ? 'bg-slate-800/80 border border-slate-700' : 'bg-white border border-slate-200'
        } focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/40 transition-all shadow-sm`}>
          <textarea
            ref={inputRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about Canadian taxes, benefits, filing..."
            rows={1}
            disabled={disabled}
            className={`flex-1 resize-none outline-none text-sm py-1 max-h-32 ${
              dark ? 'bg-transparent text-white placeholder-slate-500' : 'bg-transparent text-slate-900 placeholder-slate-400'
            }`}
            style={{ minHeight: '24px' }}
            onInput={(e) => {
              e.target.style.height = '24px';
              e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
            }}
          />
          <button
            type="submit"
            disabled={disabled || !text.trim()}
            className={`p-2 rounded-xl transition-all flex-shrink-0 ${
              text.trim() && !disabled
                ? 'bg-primary text-white hover:bg-primary-dark shadow-sm'
                : dark ? 'bg-slate-700 text-slate-500' : 'bg-slate-100 text-slate-400'
            }`}
          >
            <Send size={16} />
          </button>
        </div>
      </form>
      <p className={`text-[10px] mt-2 text-center ${dark ? 'text-slate-600' : 'text-slate-400'}`}>
        This is an educational tool, not professional tax advice. Always consult a qualified tax professional.
      </p>
    </div>
  );
}
