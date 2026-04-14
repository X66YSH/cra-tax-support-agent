import { useState } from 'react';
import confetti from 'canvas-confetti';
import { Bell, Mail, Smartphone, Calendar, Check, Clock, Loader2 } from 'lucide-react';
import { createReminder } from '../api';
import { useToast } from './Toast';

const FREQUENCIES = [
  { value: 'one-time', label: 'One-time', icon: Bell, desc: 'Single reminder' },
  { value: 'weekly', label: 'Weekly', icon: Clock, desc: 'Every week until deadline' },
  { value: 'monthly', label: 'Monthly', icon: Calendar, desc: 'Monthly until deadline' },
];

const DELIVERIES = [
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'text', label: 'Text', icon: Smartphone },
];

export default function ReminderSetup({ dark }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [frequency, setFrequency] = useState('weekly');
  const [delivery, setDelivery] = useState('email');
  const [date, setDate] = useState('2026-04-30');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { show: showToast } = useToast();

  const canSubmit = name && (delivery === 'email' ? email : phone) && date;

  const fireConfetti = () => {
    const colors = ['#6366f1', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b'];
    // Main burst from center-bottom
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.7 },
      colors,
    });
    // Side cannons
    setTimeout(() => {
      confetti({ particleCount: 40, angle: 60, spread: 55, origin: { x: 0, y: 0.8 }, colors });
      confetti({ particleCount: 40, angle: 120, spread: 55, origin: { x: 1, y: 0.8 }, colors });
    }, 200);
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setLoading(true);
    try {
      await createReminder({ name, email, phone, frequency, delivery, next_date: date });
      setDone(true);
      fireConfetti();
      showToast('Reminder set successfully!', 'success', 2500);
    } catch {
      showToast('Failed to set reminder. Try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="msg-enter rounded-2xl overflow-hidden interactive-glass max-w-lg">
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-4">
          <div className="flex items-center gap-2 text-white">
            <Check size={20} />
            <span className="font-semibold">Reminder Set!</span>
          </div>
        </div>
        <div className="p-6 text-center">
          <div className="reminder-success mx-auto w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-4">
            <Check size={32} className="text-emerald-500" />
          </div>
          <h3 className={`font-semibold text-lg mb-2 ${dark ? 'text-white' : 'text-slate-900'}`}>
            You're all set, {name}!
          </h3>
          <div className={`space-y-2 text-sm ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            <p>
              {frequency === 'one-time' ? 'A reminder' : `${frequency.charAt(0).toUpperCase() + frequency.slice(1)} reminders`} will be sent to
            </p>
            <p className={`font-medium ${dark ? 'text-indigo-400' : 'text-indigo-600'}`}>
              {delivery === 'email' ? `📧 ${email}` : `📱 ${phone}`}
            </p>
            <p>
              {frequency === 'one-time'
                ? `on ${new Date(date + 'T00:00').toLocaleDateString('en-CA', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}`
                : `starting now until ${new Date(date + 'T00:00').toLocaleDateString('en-CA', { month: 'long', day: 'numeric' })}`
              }
            </p>
          </div>
          <div className={`mt-4 p-3 rounded-xl text-xs ${dark ? 'bg-slate-700/50 text-slate-400' : 'bg-amber-50 text-amber-700'}`}>
            <strong>Don't forget:</strong> T4 slip, T2202, SIN, and any other tax documents ready before April 30!
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="msg-enter rounded-2xl overflow-hidden interactive-glass max-w-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-4">
        <div className="flex items-center gap-2 text-white">
          <Bell size={20} />
          <span className="font-semibold">Filing Reminder Setup</span>
        </div>
        <p className="text-amber-100 text-xs mt-1">Never miss the April 30 deadline</p>
      </div>

      <div className="p-5 space-y-4">
        {/* Name */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            Your Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Alex"
            className={`w-full rounded-xl px-3 py-2.5 text-sm border outline-none ${
              dark ? 'bg-slate-700/50 border-slate-600 text-white placeholder-slate-500' : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
            } focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 transition-all`}
          />
        </div>

        {/* Delivery Method */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            How should we remind you?
          </label>
          <div className="flex gap-2">
            {DELIVERIES.map((d) => (
              <button
                key={d.value}
                onClick={() => setDelivery(d.value)}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all ${
                  delivery === d.value
                    ? 'bg-amber-500 text-white border-amber-500 shadow-sm'
                    : dark
                      ? 'bg-slate-700/50 border-slate-600 text-slate-400 hover:border-slate-500'
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300'
                }`}
              >
                <d.icon size={16} />
                {d.label}
              </button>
            ))}
          </div>
        </div>

        {/* Email or Phone */}
        {delivery === 'email' ? (
          <div>
            <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@mail.utoronto.ca"
              className={`w-full rounded-xl px-3 py-2.5 text-sm border outline-none ${
                dark ? 'bg-slate-700/50 border-slate-600 text-white placeholder-slate-500' : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
              } focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 transition-all`}
            />
          </div>
        ) : (
          <div>
            <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
              Phone Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (416) 123-4567"
              className={`w-full rounded-xl px-3 py-2.5 text-sm border outline-none ${
                dark ? 'bg-slate-700/50 border-slate-600 text-white placeholder-slate-500' : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
              } focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 transition-all`}
            />
          </div>
        )}

        {/* Frequency */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            Reminder Frequency
          </label>
          <div className="grid grid-cols-3 gap-2">
            {FREQUENCIES.map((f) => (
              <button
                key={f.value}
                onClick={() => setFrequency(f.value)}
                className={`flex flex-col items-center gap-1 py-3 rounded-xl text-xs font-medium border transition-all ${
                  frequency === f.value
                    ? 'bg-amber-500 text-white border-amber-500 shadow-sm'
                    : dark
                      ? 'bg-slate-700/50 border-slate-600 text-slate-400 hover:border-slate-500'
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-slate-300'
                }`}
              >
                <f.icon size={16} />
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Deadline Date */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            <Calendar size={12} className="inline mr-1" />
            Filing Deadline
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className={`w-full rounded-xl px-3 py-2.5 text-sm border outline-none ${
              dark ? 'bg-slate-700/50 border-slate-600 text-white' : 'bg-slate-50 border-slate-200 text-slate-900'
            } focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 transition-all`}
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!canSubmit || loading}
          className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
            canSubmit && !loading
              ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:shadow-lg hover:shadow-amber-500/25 active:scale-[0.98]'
              : dark
                ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={16} className="animate-spin" />
              Setting up...
            </span>
          ) : (
            'Set Reminder'
          )}
        </button>
      </div>
    </div>
  );
}
