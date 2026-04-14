import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { CheckCircle2, X, Info, AlertCircle } from 'lucide-react';

const ToastContext = createContext(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

export function ToastProvider({ children, dark }) {
  const [toasts, setToasts] = useState([]);

  const show = useCallback((message, type = 'success', duration = 2500) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const remove = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      <div className="fixed top-4 right-4 z-[60] flex flex-col gap-2 pointer-events-none">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onClose={() => remove(t.id)} dark={dark} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onClose, dark }) {
  const icons = {
    success: <CheckCircle2 size={16} className="text-emerald-500" />,
    info: <Info size={16} className="text-blue-500" />,
    error: <AlertCircle size={16} className="text-red-500" />,
  };

  return (
    <div
      className={`toast-enter pointer-events-auto flex items-center gap-2.5 pl-3 pr-2 py-2.5 rounded-xl shadow-2xl min-w-[200px] max-w-sm ${
        dark
          ? 'bg-slate-900/80 border border-slate-700/60 text-slate-200'
          : 'bg-white/80 border border-slate-200 text-slate-800'
      }`}
      style={{ backdropFilter: 'blur(20px) saturate(180%)', WebkitBackdropFilter: 'blur(20px) saturate(180%)' }}
    >
      {icons[toast.type] || icons.info}
      <span className="text-sm font-medium flex-1">{toast.message}</span>
      <button
        onClick={onClose}
        className={`p-1 rounded-lg transition-colors ${
          dark ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-slate-100 text-slate-400'
        }`}
      >
        <X size={12} />
      </button>
    </div>
  );
}
