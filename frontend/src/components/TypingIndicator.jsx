import { Landmark } from 'lucide-react';

export default function TypingIndicator({ dark }) {
  return (
    <div className="flex gap-3 justify-start">
      <div className="bot-avatar w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
        <Landmark size={14} className="text-white" />
      </div>
      <div className={`px-4 py-3 rounded-2xl rounded-bl-md ${dark ? 'glass-bubble' : 'glass-bubble shadow-sm'}`}>
        <div className="flex gap-1.5 items-center h-5">
          <div className={`typing-dot w-2 h-2 rounded-full ${dark ? 'bg-indigo-400' : 'bg-indigo-500'}`} />
          <div className={`typing-dot w-2 h-2 rounded-full ${dark ? 'bg-indigo-400' : 'bg-indigo-500'}`} />
          <div className={`typing-dot w-2 h-2 rounded-full ${dark ? 'bg-indigo-400' : 'bg-indigo-500'}`} />
        </div>
      </div>
    </div>
  );
}
