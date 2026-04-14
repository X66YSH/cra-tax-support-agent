import { useState, useEffect } from 'react';
import { Calculator, DollarSign, MapPin, ChevronDown, ChevronUp } from 'lucide-react';

const PROVINCES = [
  'Ontario', 'British Columbia', 'Alberta', 'Quebec', 'Manitoba',
  'Saskatchewan', 'Nova Scotia', 'New Brunswick',
  'Newfoundland and Labrador', 'Prince Edward Island',
  'Northwest Territories', 'Nunavut', 'Yukon',
];

// 2024 Federal brackets
const FED_BRACKETS = [
  { min: 0, max: 55867, rate: 0.15 },
  { min: 55867, max: 111733, rate: 0.205 },
  { min: 111733, max: 154906, rate: 0.26 },
  { min: 154906, max: 220000, rate: 0.29 },
  { min: 220000, max: Infinity, rate: 0.33 },
];
const FED_PERSONAL = 15705;

// Provincial brackets (2024)
const PROV_BRACKETS = {
  'Ontario':        { brackets: [{ min: 0, max: 51446, rate: 0.0505 }, { min: 51446, max: 102894, rate: 0.0915 }, { min: 102894, max: 150000, rate: 0.1116 }, { min: 150000, max: 220000, rate: 0.1216 }, { min: 220000, max: Infinity, rate: 0.1316 }], personal: 11865 },
  'British Columbia':{ brackets: [{ min: 0, max: 45654, rate: 0.0506 }, { min: 45654, max: 91310, rate: 0.077 }, { min: 91310, max: 104835, rate: 0.105 }, { min: 104835, max: 127299, rate: 0.1229 }, { min: 127299, max: 172602, rate: 0.147 }, { min: 172602, max: 240716, rate: 0.168 }, { min: 240716, max: Infinity, rate: 0.205 }], personal: 11981 },
  'Alberta':        { brackets: [{ min: 0, max: 142292, rate: 0.10 }, { min: 142292, max: 170751, rate: 0.12 }, { min: 170751, max: 227668, rate: 0.13 }, { min: 227668, max: 341502, rate: 0.14 }, { min: 341502, max: Infinity, rate: 0.15 }], personal: 21003 },
  'Quebec':         { brackets: [{ min: 0, max: 51780, rate: 0.14 }, { min: 51780, max: 103545, rate: 0.19 }, { min: 103545, max: 126000, rate: 0.24 }, { min: 126000, max: Infinity, rate: 0.2575 }], personal: 17183 },
  'Manitoba':       { brackets: [{ min: 0, max: 47000, rate: 0.108 }, { min: 47000, max: 100000, rate: 0.1275 }, { min: 100000, max: Infinity, rate: 0.174 }], personal: 15780 },
  'Saskatchewan':   { brackets: [{ min: 0, max: 52057, rate: 0.105 }, { min: 52057, max: 148734, rate: 0.125 }, { min: 148734, max: Infinity, rate: 0.145 }], personal: 17661 },
  'Nova Scotia':    { brackets: [{ min: 0, max: 29590, rate: 0.0879 }, { min: 29590, max: 59180, rate: 0.1495 }, { min: 59180, max: 93000, rate: 0.1667 }, { min: 93000, max: 150000, rate: 0.175 }, { min: 150000, max: Infinity, rate: 0.21 }], personal: 8481 },
  'New Brunswick':  { brackets: [{ min: 0, max: 47715, rate: 0.094 }, { min: 47715, max: 95431, rate: 0.14 }, { min: 95431, max: 176756, rate: 0.16 }, { min: 176756, max: Infinity, rate: 0.195 }], personal: 12458 },
  'Newfoundland and Labrador': { brackets: [{ min: 0, max: 43198, rate: 0.087 }, { min: 43198, max: 86395, rate: 0.145 }, { min: 86395, max: 154244, rate: 0.158 }, { min: 154244, max: 215943, rate: 0.178 }, { min: 215943, max: 275870, rate: 0.198 }, { min: 275870, max: 551739, rate: 0.208 }, { min: 551739, max: 1103478, rate: 0.213 }, { min: 1103478, max: Infinity, rate: 0.218 }], personal: 10818 },
  'Prince Edward Island': { brackets: [{ min: 0, max: 32656, rate: 0.098 }, { min: 32656, max: 64313, rate: 0.138 }, { min: 64313, max: Infinity, rate: 0.167 }], personal: 12000 },
  'Northwest Territories': { brackets: [{ min: 0, max: 50597, rate: 0.059 }, { min: 50597, max: 101198, rate: 0.086 }, { min: 101198, max: 164525, rate: 0.122 }, { min: 164525, max: Infinity, rate: 0.1405 }], personal: 16593 },
  'Nunavut':        { brackets: [{ min: 0, max: 53268, rate: 0.04 }, { min: 53268, max: 106537, rate: 0.07 }, { min: 106537, max: 173205, rate: 0.09 }, { min: 173205, max: Infinity, rate: 0.115 }], personal: 17925 },
  'Yukon':          { brackets: [{ min: 0, max: 55867, rate: 0.064 }, { min: 55867, max: 111733, rate: 0.09 }, { min: 111733, max: 154906, rate: 0.109 }, { min: 154906, max: 500000, rate: 0.128 }, { min: 500000, max: Infinity, rate: 0.15 }], personal: 15705 },
};

function calcBracketTax(income, brackets, personalAmount) {
  const taxable = Math.max(0, income - personalAmount);
  let tax = 0;
  for (const b of brackets) {
    if (taxable <= b.min) break;
    const inBracket = Math.min(taxable, b.max) - b.min;
    tax += inBracket * b.rate;
  }
  return tax;
}

function fmt(n) {
  return n.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function AnimNum({ value, dark, color = '' }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const target = value || 0;
    let current = 0;
    const steps = 25;
    const inc = target / steps;
    const timer = setInterval(() => {
      current += inc;
      if (current >= target) { setDisplay(target); clearInterval(timer); }
      else setDisplay(current);
    }, 20);
    return () => clearInterval(timer);
  }, [value]);
  return <span className={color}>${fmt(display)}</span>;
}

function BarSegment({ label, amount, total, color, dark }) {
  const pct = total > 0 ? (amount / total * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <span className={`text-xs w-20 text-right ${dark ? 'text-slate-400' : 'text-slate-500'}`}>{label}</span>
      <div className={`flex-1 h-6 rounded-full overflow-hidden ${dark ? 'bg-slate-700' : 'bg-slate-100'}`}>
        <div className={`h-full rounded-full ${color} transition-all duration-700 flex items-center px-2`}
          style={{ width: `${Math.max(pct, 2)}%` }}>
          {pct > 15 && <span className="text-white text-[10px] font-medium">{pct.toFixed(1)}%</span>}
        </div>
      </div>
      <span className={`text-xs font-mono w-24 text-right ${dark ? 'text-slate-300' : 'text-slate-700'}`}>${fmt(amount)}</span>
    </div>
  );
}

export default function TaxCalculator({ dark }) {
  const [income, setIncome] = useState('');
  const [province, setProvince] = useState('Ontario');
  const [calculated, setCalculated] = useState(false);
  const [view, setView] = useState('annual'); // annual, monthly, biweekly, weekly

  const incomeNum = parseFloat(income.replace(/,/g, '')) || 0;

  const handleIncomeChange = (e) => {
    const raw = e.target.value.replace(/[^0-9]/g, '');
    setIncome(raw ? parseInt(raw).toLocaleString('en-CA') : '');
    setCalculated(false);
  };

  // Calculate taxes
  const fedTax = calcBracketTax(incomeNum, FED_BRACKETS, FED_PERSONAL);
  const provData = PROV_BRACKETS[province] || PROV_BRACKETS['Ontario'];
  const provTax = calcBracketTax(incomeNum, provData.brackets, provData.personal);
  const totalTax = fedTax + provTax;

  // CPP & EI (2024 rates for employees)
  const cppExempt = 3500;
  const cppMax = 68500;
  const cppRate = 0.0595;
  const cpp = Math.max(0, Math.min(incomeNum, cppMax) - cppExempt) * cppRate;

  const eiMax = 63200;
  const eiRate = 0.0166;
  const ei = Math.min(incomeNum, eiMax) * eiRate;

  const totalDeductions = totalTax + cpp + ei;
  const afterTax = incomeNum - totalDeductions;
  const effectiveRate = incomeNum > 0 ? (totalDeductions / incomeNum * 100) : 0;

  const divisors = { annual: 1, monthly: 12, biweekly: 26, weekly: 52 };
  const d = divisors[view];

  const viewLabels = {
    annual: 'Yearly',
    monthly: 'Monthly',
    biweekly: 'Bi-weekly',
    weekly: 'Weekly',
  };

  return (
    <div className="msg-enter rounded-2xl overflow-hidden interactive-glass max-w-lg w-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-5 py-4">
        <div className="flex items-center gap-2 text-white">
          <Calculator size={20} />
          <span className="font-semibold">Tax Estimate Calculator</span>
        </div>
        <p className="text-blue-100 text-xs mt-1">2024 Canadian tax brackets for UofT students</p>
      </div>

      <div className="p-5 space-y-4">
        {/* Income Input */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            Annual Income (CAD)
          </label>
          <div className={`flex items-center gap-2 rounded-xl px-3 py-2.5 border ${
            dark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-50 border-slate-200'
          } focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-400 transition-all`}>
            <DollarSign size={16} className={dark ? 'text-blue-400' : 'text-blue-500'} />
            <input
              type="text"
              value={income}
              onChange={handleIncomeChange}
              placeholder="e.g. 18,000"
              className={`flex-1 outline-none text-sm bg-transparent ${
                dark ? 'text-white placeholder-slate-500' : 'text-slate-900 placeholder-slate-400'
              }`}
            />
          </div>
          <div className="flex gap-2 mt-2">
            {[15000, 18000, 25000, 35000, 50000].map((v) => (
              <button
                key={v}
                onClick={() => { setIncome(v.toLocaleString('en-CA')); setCalculated(false); }}
                className={`px-2 py-1 rounded-lg text-xs transition-all ${
                  incomeNum === v
                    ? 'bg-blue-500 text-white'
                    : dark ? 'bg-slate-700 text-slate-400 hover:bg-slate-600' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                }`}
              >
                ${v/1000}k
              </button>
            ))}
          </div>
        </div>

        {/* Province */}
        <div>
          <label className={`text-xs font-medium mb-1.5 block ${dark ? 'text-slate-400' : 'text-slate-500'}`}>
            <MapPin size={12} className="inline mr-1" />Province
          </label>
          <select
            value={province}
            onChange={(e) => { setProvince(e.target.value); setCalculated(false); }}
            className={`w-full rounded-xl px-3 py-2.5 text-sm border outline-none ${
              dark ? 'bg-slate-700/50 border-slate-600 text-white' : 'bg-slate-50 border-slate-200 text-slate-900'
            } focus:ring-2 focus:ring-blue-500/20 transition-all`}
          >
            {PROVINCES.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        {/* Calculate Button */}
        {!calculated && (
          <button
            onClick={() => incomeNum > 0 && setCalculated(true)}
            disabled={!incomeNum}
            className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
              incomeNum
                ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg hover:shadow-blue-500/25 active:scale-[0.98]'
                : dark ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            }`}
          >
            Calculate My Taxes
          </button>
        )}

        {/* Results */}
        {calculated && incomeNum > 0 && (
          <div className="space-y-4 pt-2">
            {/* Big Numbers */}
            <div className="grid grid-cols-2 gap-3">
              <div className={`p-3 rounded-xl ${dark ? 'bg-slate-700/40' : 'bg-green-50'}`}>
                <p className={`text-[10px] font-medium uppercase tracking-wider ${dark ? 'text-slate-500' : 'text-slate-400'}`}>Take-Home Pay</p>
                <p className={`text-xl font-bold mt-1 ${dark ? 'text-emerald-400' : 'text-emerald-600'}`}>
                  <AnimNum value={afterTax / d} dark={dark} />
                </p>
                <p className={`text-[10px] ${dark ? 'text-slate-500' : 'text-slate-400'}`}>per {view === 'annual' ? 'year' : view === 'biweekly' ? '2 weeks' : view.replace('ly','')}</p>
              </div>
              <div className={`p-3 rounded-xl ${dark ? 'bg-slate-700/40' : 'bg-red-50'}`}>
                <p className={`text-[10px] font-medium uppercase tracking-wider ${dark ? 'text-slate-500' : 'text-slate-400'}`}>Total Deductions</p>
                <p className={`text-xl font-bold mt-1 ${dark ? 'text-red-400' : 'text-red-500'}`}>
                  <AnimNum value={totalDeductions / d} dark={dark} />
                </p>
                <p className={`text-[10px] ${dark ? 'text-slate-500' : 'text-slate-400'}`}>Effective rate: {effectiveRate.toFixed(1)}%</p>
              </div>
            </div>

            {/* Period Toggle */}
            <div className={`flex rounded-xl p-1 ${dark ? 'bg-slate-700/50' : 'bg-slate-100'}`}>
              {Object.keys(viewLabels).map((v) => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    view === v
                      ? 'bg-blue-500 text-white shadow-sm'
                      : dark ? 'text-slate-400 hover:text-slate-300' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {viewLabels[v]}
                </button>
              ))}
            </div>

            {/* Detailed Breakdown Table */}
            <div className={`rounded-xl border overflow-hidden ${dark ? 'border-slate-700' : 'border-slate-200'}`}>
              <div className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider ${
                dark ? 'bg-slate-700/60 text-slate-400' : 'bg-slate-50 text-slate-500'
              }`}>
                {viewLabels[view]} Breakdown
              </div>
              <div className="divide-y divide-slate-200 dark:divide-slate-700">
                {[
                  { label: 'Gross Income', value: incomeNum / d, bold: true },
                  { label: 'Federal Tax', value: -(fedTax / d), color: 'text-red-400' },
                  { label: `Provincial Tax (${province})`, value: -(provTax / d), color: 'text-red-400' },
                  { label: 'CPP Contributions', value: -(cpp / d), color: 'text-orange-400' },
                  { label: 'EI Premiums', value: -(ei / d), color: 'text-orange-400' },
                  { label: 'Net Income (Take-Home)', value: afterTax / d, bold: true, color: dark ? 'text-emerald-400' : 'text-emerald-600' },
                ].map((row, i) => (
                  <div key={i} className={`flex justify-between px-4 py-2.5 text-sm ${
                    row.bold ? dark ? 'bg-slate-700/30' : 'bg-slate-50/80' : ''
                  }`}>
                    <span className={`${row.bold ? 'font-semibold' : ''} ${dark ? 'text-slate-300' : 'text-slate-700'}`}>
                      {row.label}
                    </span>
                    <span className={`font-mono ${row.bold ? 'font-semibold' : ''} ${row.color || (dark ? 'text-slate-300' : 'text-slate-700')}`}>
                      {row.value < 0 ? '-' : ''}${fmt(Math.abs(row.value))}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Visual Bar Chart */}
            <div className="space-y-2">
              <p className={`text-xs font-semibold ${dark ? 'text-slate-400' : 'text-slate-500'}`}>Where Your Money Goes</p>
              <BarSegment label="Take-Home" amount={afterTax} total={incomeNum} color="bg-emerald-500" dark={dark} />
              <BarSegment label="Federal" amount={fedTax} total={incomeNum} color="bg-blue-500" dark={dark} />
              <BarSegment label="Provincial" amount={provTax} total={incomeNum} color="bg-indigo-500" dark={dark} />
              <BarSegment label="CPP" amount={cpp} total={incomeNum} color="bg-amber-500" dark={dark} />
              <BarSegment label="EI" amount={ei} total={incomeNum} color="bg-orange-500" dark={dark} />
            </div>

            {/* Disclaimer */}
            <p className={`text-[10px] leading-relaxed ${dark ? 'text-slate-600' : 'text-slate-400'}`}>
              * Estimates based on 2024 tax brackets. Does not include surtaxes, credits (tuition, GST/HST), or other deductions.
              This is for educational purposes only — consult a tax professional for your actual filing.
            </p>

            {/* Recalculate */}
            <button
              onClick={() => setCalculated(false)}
              className={`w-full py-2 rounded-xl text-xs font-medium transition-all ${
                dark ? 'bg-slate-700 text-slate-400 hover:bg-slate-600' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              }`}
            >
              Recalculate with different values
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
