import { useState } from 'react';
import { Gift, ChevronRight, Loader2, CheckCircle, XCircle, DollarSign } from 'lucide-react';
import { callAction } from '../api';

const STEPS = [
  { key: 'residency_status', question: 'What is your tax residency status?', options: [
    { value: 'resident', label: 'Canadian Tax Resident', desc: 'Lived in Canada or have significant ties' },
    { value: 'non-resident', label: 'Non-Resident', desc: 'No significant ties to Canada' },
  ]},
  { key: 'annual_income', question: 'What is your annual income (CAD)?', type: 'income' },
  { key: 'is_student', question: 'Are you enrolled at a Canadian post-secondary institution?', options: [
    { value: true, label: 'Yes, I\'m a student', desc: 'Currently enrolled at UofT or other institution' },
    { value: false, label: 'No', desc: 'Not currently enrolled' },
  ]},
  { key: 'has_tuition', question: 'Do you have a T2202 tuition certificate?', options: [
    { value: true, label: 'Yes, I have it', desc: 'T2202 from my school' },
    { value: false, label: 'No / Not sure', desc: 'Don\'t have or haven\'t checked' },
  ]},
];

export default function BenefitChecker({ dark }) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [income, setIncome] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const current = STEPS[step];
  const progress = ((step) / STEPS.length) * 100;

  const handleSelect = (value) => {
    const updated = { ...answers, [current.key]: value };
    setAnswers(updated);

    if (step < STEPS.length - 1) {
      setStep(step + 1);
    } else {
      submitCheck(updated);
    }
  };

  const handleIncomeSubmit = () => {
    const num = parseFloat(income.replace(/,/g, '')) || 0;
    if (!num) return;
    handleSelect(num);
  };

  const submitCheck = async (params) => {
    setLoading(true);
    try {
      const data = await callAction('benefit_eligibility', params);
      setResult(data.result);
    } catch {
      setResult('Sorry, something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`msg-enter rounded-2xl overflow-hidden border max-w-lg ${
        dark ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
      }`}>
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-4">
          <div className="flex items-center gap-2 text-white">
            <Gift size={20} />
            <span className="font-semibold">Checking Eligibility...</span>
          </div>
        </div>
        <div className="p-10 flex flex-col items-center gap-3">
          <Loader2 size={32} className="animate-spin text-emerald-500" />
          <p className={`text-sm ${dark ? 'text-slate-400' : 'text-slate-500'}`}>Analyzing your profile with AI...</p>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <div className={`msg-enter rounded-2xl overflow-hidden border max-w-lg ${
        dark ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
      }`}>
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-4">
          <div className="flex items-center gap-2 text-white">
            <CheckCircle size={20} />
            <span className="font-semibold">Eligibility Results</span>
          </div>
        </div>
        <div className="p-5">
          <div className={`text-sm leading-relaxed whitespace-pre-wrap ${dark ? 'text-slate-300' : 'text-slate-700'}`}>
            {result}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`msg-enter rounded-2xl overflow-hidden border max-w-lg ${
      dark ? 'bg-slate-800/60 border-slate-700' : 'bg-white border-slate-200'
    }`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-4">
        <div className="flex items-center gap-2 text-white">
          <Gift size={20} />
          <span className="font-semibold">Benefit Eligibility Checker</span>
        </div>
        <p className="text-emerald-100 text-xs mt-1">GST/HST Credit, OTB, Tuition Credits</p>
      </div>

      {/* Progress bar */}
      <div className={`h-1 ${dark ? 'bg-slate-700' : 'bg-slate-100'}`}>
        <div
          className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="p-5">
        {/* Step indicator */}
        <p className={`text-xs mb-1 ${dark ? 'text-slate-500' : 'text-slate-400'}`}>
          Step {step + 1} of {STEPS.length}
        </p>
        <h3 className={`text-sm font-semibold mb-4 ${dark ? 'text-white' : 'text-slate-900'}`}>
          {current.question}
        </h3>

        {current.type === 'income' ? (
          <div className="space-y-3">
            <div className={`flex items-center gap-2 rounded-xl px-3 py-2.5 border ${
              dark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-50 border-slate-200'
            } focus-within:ring-2 focus-within:ring-emerald-500/20`}>
              <DollarSign size={16} className="text-emerald-500" />
              <input
                type="text"
                value={income}
                onChange={(e) => {
                  const raw = e.target.value.replace(/[^0-9]/g, '');
                  setIncome(raw ? parseInt(raw).toLocaleString('en-CA') : '');
                }}
                placeholder="e.g. 25,000"
                className={`flex-1 outline-none text-sm bg-transparent ${
                  dark ? 'text-white placeholder-slate-500' : 'text-slate-900 placeholder-slate-400'
                }`}
                onKeyDown={(e) => e.key === 'Enter' && handleIncomeSubmit()}
              />
            </div>
            <button
              onClick={handleIncomeSubmit}
              disabled={!income}
              className={`w-full py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${
                income
                  ? 'bg-emerald-500 text-white hover:bg-emerald-600 active:scale-[0.98]'
                  : dark ? 'bg-slate-700 text-slate-500' : 'bg-slate-100 text-slate-400'
              }`}
            >
              Continue <ChevronRight size={16} />
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {current.options.map((opt) => (
              <button
                key={String(opt.value)}
                onClick={() => handleSelect(opt.value)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left border transition-all hover:scale-[1.01] active:scale-[0.99] ${
                  dark
                    ? 'bg-slate-700/30 border-slate-600 hover:border-emerald-500/50 hover:bg-slate-700/60'
                    : 'bg-slate-50 border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/50'
                }`}
              >
                <div>
                  <p className={`text-sm font-medium ${dark ? 'text-white' : 'text-slate-800'}`}>{opt.label}</p>
                  <p className={`text-xs mt-0.5 ${dark ? 'text-slate-500' : 'text-slate-400'}`}>{opt.desc}</p>
                </div>
                <ChevronRight size={16} className={`ml-auto ${dark ? 'text-slate-600' : 'text-slate-300'}`} />
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
