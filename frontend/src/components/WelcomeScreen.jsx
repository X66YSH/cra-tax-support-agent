import { Calculator, Gift, Bell, CalendarCheck } from 'lucide-react';

const suggestions = [
  { icon: Calculator, text: 'Estimate my taxes as a TA earning $18k', label: 'Tax Estimate', desc: 'Calculate federal & provincial tax', gradient: 'from-blue-500 to-indigo-500' },
  { icon: Gift, text: 'Am I eligible for the GST/HST credit?', label: 'Benefit Check', desc: 'GST/HST, OTB, tuition credits', gradient: 'from-emerald-500 to-teal-500' },
  { icon: Bell, text: 'When is the tax filing deadline?', label: 'Filing Reminder', desc: 'Deadlines and filing checklist', gradient: 'from-amber-500 to-orange-500' },
  { icon: CalendarCheck, text: 'Book a UTSU tax clinic appointment', label: 'Book Clinic', desc: 'Free UTSU/CVITP tax help', gradient: 'from-purple-500 to-pink-500' },
];

// Track mouse for spotlight + 3D tilt effects on cards
const handleMouseMove = (e) => {
  const el = e.currentTarget;
  const rect = el.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  // Spotlight position
  el.style.setProperty('--mx', `${x}px`);
  el.style.setProperty('--my', `${y}px`);

  // 3D tilt — range ±8 degrees, flipped so card tilts toward cursor
  const cx = rect.width / 2;
  const cy = rect.height / 2;
  const ry = ((x - cx) / cx) * 8;  // rotateY
  const rx = -((y - cy) / cy) * 8; // rotateX (inverted)
  el.style.setProperty('--rx', `${rx}deg`);
  el.style.setProperty('--ry', `${ry}deg`);
};

const handleMouseLeave = (e) => {
  const el = e.currentTarget;
  el.style.setProperty('--rx', '0deg');
  el.style.setProperty('--ry', '0deg');
};

export default function WelcomeScreen({ onSuggestion, dark }) {
  return (
    <div className="welcome-bg flex-1 flex flex-col items-center justify-center px-6">
      {/* Animated background blobs */}
      <div className="welcome-blob welcome-blob-1" />
      <div className="welcome-blob welcome-blob-2" />
      <div className="welcome-blob welcome-blob-3" />

      {/* Content (above blobs) */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Logo */}
        <img src="/logo.svg" alt="CRA Tax Support" className="w-20 h-20 rounded-2xl shadow-lg mb-6 stagger-item" />

        <h2 className="text-3xl font-bold mb-2 gradient-text stagger-item">
          CRA Tax Support Agent
        </h2>
        <p className={`text-sm mb-10 max-w-md text-center leading-relaxed stagger-item ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
          AI-powered Canadian tax assistant built for University of Toronto students.
          Ask questions, estimate taxes, check benefits, or book a free tax clinic.
        </p>

        {/* Action cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => onSuggestion(s.text)}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
              className={`group spotlight tilt-card stagger-item flex items-start gap-3 px-4 py-4 rounded-2xl text-left transition-all hover:shadow-lg ${
                dark
                  ? 'bg-slate-800/60 border border-slate-700/60 hover:border-slate-600 backdrop-blur-sm'
                  : 'bg-white/80 border border-slate-200 hover:border-slate-300 backdrop-blur-sm'
              }`}
            >
              <div className={`relative z-10 w-10 h-10 rounded-xl bg-gradient-to-br ${s.gradient} flex items-center justify-center flex-shrink-0 shadow-sm`}>
                <s.icon size={18} className="text-white" />
              </div>
              <div className="relative z-10">
                <span className={`text-sm font-semibold block ${dark ? 'text-white' : 'text-slate-800'}`}>
                  {s.label}
                </span>
                <span className={`text-xs mt-0.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
                  {s.desc}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
