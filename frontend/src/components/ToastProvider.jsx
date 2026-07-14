import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

let pushToast = null;

export function toast(message, type = 'success') {
  if (pushToast) pushToast({ id: Date.now() + Math.random(), message, type });
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    pushToast = (t) => {
      setToasts((prev) => [...prev.slice(-4), t]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== t.id));
      }, 3400);
    };
    return () => {
      pushToast = null;
    };
  }, []);

  return (
    <>
      {children}
      {createPortal(
        <div className="fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2">
          {toasts.map((t) => (
            <div
              key={t.id}
              className={`animate-fadeIn rounded-xl border px-4 py-3 text-sm shadow-card ${
                t.type === 'error'
                  ? 'border-red-200 bg-red-50 text-red-800'
                  : t.type === 'info'
                    ? 'border-sky-200 bg-sky-50 text-sky-900'
                    : 'border-brand-200 bg-white text-ink-800'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <p>{t.message}</p>
                <button
                  className="text-xs opacity-60 hover:opacity-100"
                  onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>,
        document.body
      )}
    </>
  );
}
