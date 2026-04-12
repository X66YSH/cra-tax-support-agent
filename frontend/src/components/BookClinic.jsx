import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { CalendarCheck, FileText, Check, X, Loader2, ExternalLink } from 'lucide-react';
import { callAction } from '../api';

export default function BookClinic({ dark }) {
  const [studentType, setStudentType] = useState(null);
  const [income, setIncome] = useState('');
  const [docs, setDocs] = useState({ has_complex_taxes: false, has_sin: false, has_t4: false, has_t2202: false });
  const [step, setStep] = useState(0); // 0: type, 1: income, 2: docs, 3: result
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const toggleDoc = (key) => setDocs((d) => ({ ...d, [key]: !d[key] }));

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const data = await callAction('book_appointment', {
        student_type: studentType,
        annual_income: parseFloat(income.replace(/,/g, '')) || 0,
        ...docs,
      });
      setResult(data.result);
      setStep(3);
    } catch {
      setResult('Something went wrong. Please try again.');
      setStep(3);
    } finally {
      setLoading(false);
    }
  };

  const docItems = [
    { key: 'has_sin', label: 'Social Insurance Number (SIN)', desc: 'Required for filing' },
    { key: 'has_t4', label: 'T4 Slip', desc: 'Employment income statement' },
    { key: 'has_t2202', label: 'T2202 Tuition Certificate', desc: 'From UofT for tuition credits' },
    { key: 'has_complex_taxes', label: 'Complex tax situation', desc: 'Self-employment, foreign income >$1k, or capital gains' },
  ];

  const readyCount = [docs.has_sin, docs.has_t4, docs.has_t2202].filter(Boolean).length;

  return (
    <div className={`msg-enter rounded-2xl overflow-hidden border max-w-lg ${
      dark ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
    }`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 px-5 py-4">
        <div className="flex items-center gap-2 text-white">
          <CalendarCheck size={20} />
          <span className="font-semibold">Book UTSU Tax Clinic</span>
        </div>
        <p className="text-purple-100 text-xs mt-1">Free tax filing help for UofT students (CVITP)</p>
      </div>

      {/* Progress dots */}
      <div className="flex items-center justify-center gap-2 py-3">
        {[0, 1, 2, 3].map((s) => (
          <div key={s} className={`h-1.5 rounded-full transition-all duration-300 ${
            s <= step
              ? 'bg-purple-500 w-8'
              : dark ? 'bg-slate-700 w-4' : 'bg-slate-200 w-4'
          }`} />
        ))}
      </div>

      <div className="p-5">
        {/* Step 0: Student Type */}
        {step === 0 && (
          <div className="space-y-3">
            <h3 className={`text-sm font-semibold ${dark ? 'text-white' : 'text-slate-900'}`}>
              What type of student are you?
            </h3>
            {['undergrad', 'grad'].map((type) => (
              <button
                key={type}
                onClick={() => { setStudentType(type); setStep(1); }}
                className={`w-full px-4 py-3 rounded-xl text-left border transition-all hover:scale-[1.01] ${
                  dark
                    ? 'bg-slate-700/30 border-slate-600 hover:border-purple-500/50'
                    : 'bg-slate-50 border-slate-200 hover:border-purple-400'
                }`}
              >
                <p className={`text-sm font-medium ${dark ? 'text-white' : 'text-slate-800'}`}>
                  {type === 'undergrad' ? '🎓 Undergraduate' : '🔬 Graduate'}
                </p>
                <p className={`text-xs mt-0.5 ${dark ? 'text-slate-500' : 'text-slate-400'}`}>
                  {type === 'undergrad' ? 'Bachelor\'s program' : 'Master\'s or PhD program'}
                </p>
              </button>
            ))}
          </div>
        )}

        {/* Step 1: Income */}
        {step === 1 && (
          <div className="space-y-3">
            <h3 className={`text-sm font-semibold ${dark ? 'text-white' : 'text-slate-900'}`}>
              What's your annual income?
            </h3>
            <div className={`flex items-center gap-2 rounded-xl px-3 py-2.5 border ${
              dark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-50 border-slate-200'
            } focus-within:ring-2 focus-within:ring-purple-500/20`}>
              <span className="text-purple-500 font-medium">$</span>
              <input
                type="text"
                value={income}
                onChange={(e) => {
                  const raw = e.target.value.replace(/[^0-9]/g, '');
                  setIncome(raw ? parseInt(raw).toLocaleString('en-CA') : '');
                }}
                placeholder="e.g. 18,000"
                className={`flex-1 outline-none text-sm bg-transparent ${
                  dark ? 'text-white placeholder-slate-500' : 'text-slate-900 placeholder-slate-400'
                }`}
                onKeyDown={(e) => e.key === 'Enter' && income && setStep(2)}
              />
            </div>
            <button
              onClick={() => setStep(2)}
              disabled={!income}
              className={`w-full py-2.5 rounded-xl text-sm font-medium transition-all ${
                income
                  ? 'bg-purple-500 text-white hover:bg-purple-600 active:scale-[0.98]'
                  : dark ? 'bg-slate-700 text-slate-500' : 'bg-slate-100 text-slate-400'
              }`}
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Document Checklist */}
        {step === 2 && (
          <div className="space-y-3">
            <h3 className={`text-sm font-semibold ${dark ? 'text-white' : 'text-slate-900'}`}>
              Document Checklist
            </h3>
            <p className={`text-xs ${dark ? 'text-slate-500' : 'text-slate-400'}`}>
              Toggle the documents you have ready ({readyCount}/3 required docs)
            </p>
            <div className="space-y-2">
              {docItems.map((d) => (
                <button
                  key={d.key}
                  onClick={() => toggleDoc(d.key)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all ${
                    docs[d.key]
                      ? d.key === 'has_complex_taxes'
                        ? dark ? 'bg-amber-900/20 border-amber-700/50' : 'bg-amber-50 border-amber-200'
                        : dark ? 'bg-purple-900/20 border-purple-700/50' : 'bg-purple-50 border-purple-200'
                      : dark ? 'bg-slate-700/30 border-slate-600' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    docs[d.key]
                      ? d.key === 'has_complex_taxes' ? 'bg-amber-500 text-white' : 'bg-purple-500 text-white'
                      : dark ? 'bg-slate-600 text-slate-400' : 'bg-slate-200 text-slate-400'
                  }`}>
                    {docs[d.key] ? <Check size={14} /> : <X size={14} />}
                  </div>
                  <div className="text-left">
                    <p className={`text-sm font-medium ${dark ? 'text-white' : 'text-slate-800'}`}>
                      <FileText size={12} className="inline mr-1" />{d.label}
                    </p>
                    <p className={`text-xs ${dark ? 'text-slate-500' : 'text-slate-400'}`}>{d.desc}</p>
                  </div>
                </button>
              ))}
            </div>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
                !loading
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/25 active:scale-[0.98]'
                  : dark ? 'bg-slate-700 text-slate-500' : 'bg-slate-100 text-slate-400'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 size={16} className="animate-spin" /> Checking eligibility...
                </span>
              ) : 'Check Eligibility & Book'}
            </button>
          </div>
        )}

        {/* Step 3: Result */}
        {step === 3 && result && (
          <div className="space-y-4">
            <div className={`message-content text-sm leading-relaxed ${dark ? 'text-slate-300' : 'text-slate-700'}`}>
              <ReactMarkdown
                components={{
                  a: ({ href, children }) => (
                    <a href={href} target="_blank" rel="noopener noreferrer"
                      className="text-purple-500 dark:text-purple-400 underline hover:text-purple-700">
                      {children}
                    </a>
                  ),
                }}
              >
                {result}
              </ReactMarkdown>
            </div>
            <a
              href="https://www.utsu.ca/tax"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm font-semibold bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/25 transition-all active:scale-[0.98]"
            >
              <CalendarCheck size={16} />
              Book on UTSU Website
              <ExternalLink size={14} />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
