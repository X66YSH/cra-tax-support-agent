import { useEffect } from 'react';
import { X, ExternalLink, FileText } from 'lucide-react';

// Clean up PDF extraction artifacts: merge broken lines, collapse whitespace
function cleanText(text) {
  if (!text) return '';
  return text
    // Join lines that look like mid-sentence breaks (lowercase/comma after newline)
    .replace(/\n([a-z,.;:)\]])/g, ' $1')
    // Join lines that break before a lowercase word
    .replace(/([a-z,])\n+([a-z])/g, '$1 $2')
    // Collapse 3+ newlines to 2 (paragraph break)
    .replace(/\n{3,}/g, '\n\n')
    // Collapse multiple spaces
    .replace(/ {2,}/g, ' ')
    // Trim each line
    .split('\n')
    .map((line) => line.trim())
    .join('\n')
    .trim();
}

// Extract meaningful keywords from the user's query for highlighting
function extractKeywords(query) {
  if (!query) return [];
  const stopwords = new Set([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'of', 'in', 'on', 'at', 'to',
    'for', 'with', 'by', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
    'whom', 'this', 'that', 'these', 'those', 'am', 'or', 'and', 'but',
    'if', 'as', 'so', 'than', 'too', 'very', 'just', 'not', 'no', 'yes',
    'how', 'when', 'where', 'why', 'my', 'your', 'their', 'our', 'me',
  ]);
  return query
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2 && !stopwords.has(w));
}

// Highlight matching keywords in text
function HighlightedText({ text, keywords, dark }) {
  if (!keywords.length) return <span>{text}</span>;

  // Build a regex that matches any keyword (case-insensitive)
  const escaped = keywords.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = new RegExp(`\\b(${escaped.join('|')})\\b`, 'gi');

  const parts = text.split(pattern);

  return (
    <span>
      {parts.map((part, i) => {
        const isMatch = keywords.some(
          (k) => part.toLowerCase() === k.toLowerCase()
        );
        if (isMatch) {
          return (
            <mark
              key={i}
              className={`rounded px-0.5 ${
                dark
                  ? 'bg-amber-500/30 text-amber-200'
                  : 'bg-amber-200 text-amber-900'
              }`}
            >
              {part}
            </mark>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}

export default function SourcePreview({ source, onClose, dark }) {
  useEffect(() => {
    const handleEsc = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!source) return null;

  const keywords = extractKeywords(source.query);
  const cleanedText = cleanText(source.text);
  const scorePercent = Math.round((source.score || 0) * 100);

  // Split into paragraphs for better visual structure
  const paragraphs = cleanedText.split(/\n\n+/).filter((p) => p.trim());

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Slide-out sheet */}
      <div
        className={`fixed right-0 top-0 h-screen w-full md:w-[500px] lg:w-[600px] z-50 flex flex-col shadow-2xl animate-slide-in-right ${
          dark
            ? 'bg-slate-900 border-l border-slate-800'
            : 'bg-white border-l border-slate-200'
        }`}
      >
        {/* Header */}
        <div
          className={`flex items-start justify-between gap-3 px-5 py-4 border-b ${
            dark ? 'border-slate-800' : 'border-slate-200'
          }`}
        >
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div
              className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                dark ? 'bg-indigo-500/20 text-indigo-400' : 'bg-indigo-50 text-indigo-600'
              }`}
            >
              <FileText size={16} />
            </div>
            <div className="flex-1 min-w-0">
              <p
                className={`text-xs font-medium mb-0.5 ${
                  dark ? 'text-slate-500' : 'text-slate-400'
                }`}
              >
                Source Preview
              </p>
              <h3
                className={`text-sm font-semibold leading-tight ${
                  dark ? 'text-white' : 'text-slate-900'
                }`}
              >
                {source.title}
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-1.5 rounded-lg transition-colors flex-shrink-0 ${
              dark
                ? 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
            }`}
            title="Close (Esc)"
          >
            <X size={18} />
          </button>
        </div>

        {/* Relevance score */}
        <div
          className={`px-5 py-3 border-b ${
            dark ? 'border-slate-800' : 'border-slate-200'
          }`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <span
              className={`text-xs font-medium cursor-help ${
                dark ? 'text-slate-400' : 'text-slate-500'
              }`}
              title="Cosine similarity between your query and this passage, computed by all-MiniLM-L6-v2 embeddings"
            >
              Relevance Score
              <span className="ml-1 opacity-60">ⓘ</span>
            </span>
            <span
              className={`text-xs font-semibold ${
                dark ? 'text-indigo-400' : 'text-indigo-600'
              }`}
            >
              {scorePercent}%
            </span>
          </div>
          <div
            className={`h-1.5 rounded-full overflow-hidden ${
              dark ? 'bg-slate-800' : 'bg-slate-100'
            }`}
          >
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-cyan-500 transition-all duration-500"
              style={{ width: `${scorePercent}%` }}
            />
          </div>
        </div>

        {/* Chunk text with keyword highlighting */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          <div
            className={`text-xs font-semibold uppercase tracking-wide mb-2 ${
              dark ? 'text-slate-500' : 'text-slate-400'
            }`}
          >
            Retrieved Passage
          </div>
          <div
            className={`text-sm leading-relaxed rounded-xl p-4 space-y-3 ${
              dark
                ? 'bg-slate-800/60 text-slate-200 border border-slate-700/50'
                : 'bg-slate-50 text-slate-700 border border-slate-200'
            }`}
          >
            {source.text && paragraphs.length > 0 ? (
              paragraphs.map((para, i) => (
                <p key={i}>
                  <HighlightedText text={para} keywords={keywords} dark={dark} />
                </p>
              ))
            ) : (
              <span className={dark ? 'text-slate-500 italic' : 'text-slate-400 italic'}>
                Full passage text not available for this source. Click below to view on CRA website.
              </span>
            )}
          </div>

          {keywords.length > 0 && (
            <div className="mt-4">
              <div
                className={`text-xs font-semibold uppercase tracking-wide mb-2 ${
                  dark ? 'text-slate-500' : 'text-slate-400'
                }`}
              >
                Matched Keywords
              </div>
              <div className="flex flex-wrap gap-1.5">
                {keywords.map((k, i) => (
                  <span
                    key={i}
                    className={`text-[11px] px-2 py-0.5 rounded-full ${
                      dark
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-amber-100 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {k}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer with external link */}
        <div
          className={`px-5 py-4 border-t ${
            dark ? 'border-slate-800' : 'border-slate-200'
          }`}
        >
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-indigo-500 to-cyan-500 text-white hover:shadow-lg hover:shadow-indigo-500/25 transition-all active:scale-[0.98]"
          >
            <ExternalLink size={14} />
            View Original on CRA Website
          </a>
        </div>
      </div>
    </>
  );
}
