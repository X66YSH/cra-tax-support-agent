import { useState, useRef, useEffect } from 'react';
import { Send, Calculator, Gift, Bell, CalendarCheck } from 'lucide-react';
import InputSuggestions from './InputSuggestions';

const actions = [
  { icon: Calculator, label: 'Tax Estimate', message: 'I want to estimate my taxes', lightColor: 'text-blue-600', darkColor: 'text-blue-300', lightBg: 'bg-blue-50/70 border-blue-200/60', darkBg: 'glass-chip-blue' },
  { icon: Gift, label: 'Benefits', message: 'Check my benefit eligibility', lightColor: 'text-emerald-600', darkColor: 'text-emerald-300', lightBg: 'bg-emerald-50/70 border-emerald-200/60', darkBg: 'glass-chip-emerald' },
  { icon: Bell, label: 'Filing', message: 'Set up a filing reminder for me', lightColor: 'text-amber-600', darkColor: 'text-amber-300', lightBg: 'bg-amber-50/70 border-amber-200/60', darkBg: 'glass-chip-amber' },
  { icon: CalendarCheck, label: 'Book Clinic', message: 'I want to book a tax clinic appointment', lightColor: 'text-purple-600', darkColor: 'text-purple-300', lightBg: 'bg-purple-50/70 border-purple-200/60', darkBg: 'glass-chip-purple' },
];

export default function ChatInput({ onSend, disabled, dark, activeAction }) {
  const [text, setText] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
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
    setShowSuggestions(false);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleSelectSuggestion = (suggestion) => {
    setText('');
    setShowSuggestions(false);
    onSend(suggestion);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`border-t px-4 py-3 header-blur ${dark ? 'border-slate-800/50' : 'border-slate-200/50'}`}>
      {/* Action chips — always visible */}
      <div className="flex gap-2 mb-3 overflow-x-auto overflow-y-visible pb-1 pt-1 px-1 -mx-1">
        {actions.map((a, i) => (
          <button
            key={i}
            onClick={() => !disabled && onSend(a.message)}
            disabled={disabled}
            className={`action-chip action-chip-magnetic flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border whitespace-nowrap transition-opacity ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            } ${dark ? a.darkBg : a.lightBg} ${dark ? a.darkColor : a.lightColor}`}
          >
            <a.icon size={13} />
            {a.label}
          </button>
        ))}
      </div>

      {/* Input with AI suggestions dropdown */}
      <form onSubmit={handleSubmit} className="relative">
        {showSuggestions && !disabled && text.trim().length >= 2 && (
          <InputSuggestions
            query={text}
            onSelect={handleSelectSuggestion}
            dark={dark}
          />
        )}
        <div className={`input-glow flex items-end gap-2 rounded-2xl px-4 py-2.5 glass-bubble ${
          dark ? 'border border-slate-700/50' : 'border border-slate-200'
        } transition-all shadow-sm`}>
          <textarea
            ref={inputRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
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
