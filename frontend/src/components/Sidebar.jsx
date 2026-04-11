import { useState } from 'react';
import { Plus, Trash2, MessageSquare, Sun, Moon } from 'lucide-react';

export default function Sidebar({ sessions, activeId, onSelect, onCreate, onDelete, dark, onToggleDark }) {
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (confirmDelete === id) {
      onDelete(id);
      setConfirmDelete(null);
    } else {
      setConfirmDelete(id);
      // Auto-dismiss after 3 seconds
      setTimeout(() => setConfirmDelete(null), 3000);
    }
  };

  return (
    <div className={`w-72 h-screen flex flex-col border-r ${dark ? 'bg-sidebar-dark border-slate-800' : 'bg-sidebar border-slate-200'}`}>
      {/* Header */}
      <div className={`p-4 border-b ${dark ? 'border-slate-800' : 'border-slate-200'}`}>
        <div className="flex items-center gap-3 mb-4">
          <img src="/logo.svg" alt="CRA Tax" className="w-9 h-9 rounded-xl shadow-sm" />
          <div>
            <h1 className={`text-sm font-semibold ${dark ? 'text-white' : 'text-slate-900'}`}>CRA Tax Support</h1>
            <p className={`text-xs ${dark ? 'text-slate-500' : 'text-slate-500'}`}>UofT Student Assistant</p>
          </div>
        </div>
        <button
          onClick={onCreate}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-white bg-primary hover:bg-primary-dark transition-colors shadow-sm"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {sessions.length === 0 && (
          <p className={`text-xs text-center mt-8 ${dark ? 'text-slate-600' : 'text-slate-400'}`}>
            No conversations yet
          </p>
        )}
        {sessions.map((s) => (
          <div
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 ${
              s.id === activeId
                ? dark ? 'bg-slate-800 shadow-sm' : 'bg-indigo-50 shadow-sm'
                : dark ? 'hover:bg-slate-800/60' : 'hover:bg-slate-50'
            }`}
          >
            <MessageSquare size={14} className={
              s.id === activeId
                ? dark ? 'text-indigo-400' : 'text-indigo-500'
                : dark ? 'text-slate-500' : 'text-slate-400'
            } />
            <span className={`flex-1 text-sm truncate ${
              s.id === activeId
                ? dark ? 'text-white font-medium' : 'text-indigo-900 font-medium'
                : dark ? 'text-slate-300' : 'text-slate-600'
            }`}>
              {s.title}
            </span>
            <button
              onClick={(e) => handleDelete(e, s.id)}
              className={`p-1 rounded-lg transition-all ${
                confirmDelete === s.id
                  ? 'opacity-100 bg-red-500/20 text-red-400'
                  : `opacity-0 group-hover:opacity-100 ${dark ? 'hover:bg-slate-700 text-slate-500' : 'hover:bg-slate-200 text-slate-400'}`
              }`}
              title={confirmDelete === s.id ? 'Click again to confirm' : 'Delete'}
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className={`p-3 border-t ${dark ? 'border-slate-800' : 'border-slate-200'}`}>
        <button
          onClick={onToggleDark}
          className={`flex items-center gap-2 w-full px-3 py-2 rounded-xl text-sm transition-colors ${
            dark ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          {dark ? <Sun size={14} /> : <Moon size={14} />}
          {dark ? 'Light mode' : 'Dark mode'}
        </button>
      </div>
    </div>
  );
}
