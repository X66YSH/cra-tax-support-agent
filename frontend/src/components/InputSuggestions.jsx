import { Sparkles, ArrowUpRight } from 'lucide-react';

const ALL_SUGGESTIONS = [
  { text: 'When is the tax filing deadline?', category: 'Deadlines' },
  { text: 'What is the basic personal amount for 2024?', category: 'Amounts' },
  { text: 'How do I carry forward my tuition tax credit?', category: 'Tuition' },
  { text: 'Am I eligible for the GST/HST credit as an international student?', category: 'Benefits' },
  { text: 'What documents do I need to file my taxes?', category: 'Filing' },
  { text: 'How do I report scholarship income on my tax return?', category: 'Students' },
  { text: 'What is a T2202 tuition certificate?', category: 'Slips' },
  { text: 'Do international students pay taxes in Canada?', category: 'Students' },
  { text: 'How much tax do I owe on $18,000 in Ontario?', category: 'Calculate' },
  { text: 'Can I claim moving expenses for coming to UofT?', category: 'Deductions' },
  { text: 'What is the Ontario Trillium Benefit?', category: 'Benefits' },
  { text: 'How do I get a SIN as a student?', category: 'Documents' },
  { text: 'What tax software can I use for free?', category: 'Filing' },
  { text: 'What is a T4 slip?', category: 'Slips' },
  { text: 'Do I need to file taxes if I had no income?', category: 'Filing' },
];

function getSuggestions(query, limit = 4) {
  if (!query || query.trim().length < 2) {
    // Empty query — show popular suggestions
    return ALL_SUGGESTIONS.slice(0, limit);
  }

  const q = query.toLowerCase().trim();
  const tokens = q.split(/\s+/).filter((t) => t.length > 1);

  // Score each suggestion by token overlap
  const scored = ALL_SUGGESTIONS.map((s) => {
    const text = s.text.toLowerCase();
    let score = 0;
    // Exact substring match = high score
    if (text.includes(q)) score += 10;
    // Token matches
    for (const t of tokens) {
      if (text.includes(t)) score += 2;
    }
    return { ...s, score };
  });

  return scored
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

export default function InputSuggestions({ query, onSelect, dark }) {
  const suggestions = getSuggestions(query);

  if (suggestions.length === 0) return null;

  return (
    <div className="suggestion-dropdown suggestion-glass absolute bottom-full left-0 right-0 mb-2 rounded-2xl overflow-hidden">
      <div
        className={`flex items-center gap-2 px-4 py-2 text-[11px] font-semibold uppercase tracking-wide border-b ${
          dark ? 'text-indigo-300 border-white/5' : 'text-indigo-600 border-white/40'
        }`}
      >
        <Sparkles size={12} />
        {query && query.trim().length >= 2 ? 'Suggested questions' : 'Popular questions'}
      </div>
      <div className="py-1 max-h-64 overflow-y-auto">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onMouseDown={(e) => {
              e.preventDefault(); // prevent textarea blur
              onSelect(s.text);
            }}
            className={`w-full flex items-center justify-between gap-3 px-4 py-2.5 text-left text-sm transition-colors group ${
              dark
                ? 'hover:bg-white/5 text-slate-100'
                : 'hover:bg-white/40 text-slate-800'
            }`}
          >
            <div className="flex-1 min-w-0">
              <p className="truncate">{s.text}</p>
              <p className={`text-[10px] mt-0.5 ${dark ? 'text-slate-500' : 'text-slate-400'}`}>
                {s.category}
              </p>
            </div>
            <ArrowUpRight
              size={14}
              className={`flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity ${
                dark ? 'text-indigo-400' : 'text-indigo-500'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
