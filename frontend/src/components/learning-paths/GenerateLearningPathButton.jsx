// File: frontend/src/components/learning-paths/GenerateLearningPathButton.jsx
// Description: CTA button for generating new learning paths
// Why: Prominent call-to-action to encourage path generation
// Relevant Files: app/learning-paths/page.jsx

'use client';

import { Sparkles } from 'lucide-react';

export default function GenerateLearningPathButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
    >
      <Sparkles className="w-5 h-5" />
      Generate New Path
    </button>
  );
}
