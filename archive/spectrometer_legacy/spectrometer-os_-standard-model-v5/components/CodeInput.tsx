
import React, { useState } from 'react';
import { X, Play, FileCode, AlertCircle } from 'lucide-react';
import { Theme } from '../types';

interface CodeInputProps {
    theme: Theme;
    onClose: () => void;
    onAnalyze: (code: string) => void;
}

export const CodeInput: React.FC<CodeInputProps> = ({ theme, onClose, onAnalyze }) => {
    const [code, setCode] = useState('');
    const isLight = theme === 'light';

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-10 pointer-events-auto">
            <div className={`absolute inset-0 backdrop-blur-md ${isLight ? 'bg-white/60' : 'bg-black/60'}`} onClick={onClose} />
            
            <div className={`relative w-full max-w-4xl h-full max-h-[80vh] shadow-2xl rounded-xl border flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200 ${isLight ? 'bg-white border-stone-200' : 'bg-stone-900 border-stone-800'}`}>
                
                {/* Header */}
                <div className={`p-5 border-b flex justify-between items-center ${isLight ? 'border-stone-100 bg-stone-50/50' : 'border-stone-800 bg-stone-950/50'}`}>
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isLight ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-900'}`}>
                            <FileCode size={20} />
                        </div>
                        <div>
                            <h2 className={`text-lg font-bold leading-tight ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>Source Code Injection</h2>
                            <p className={`text-xs font-mono uppercase tracking-wide ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>
                                Paste your code to generate a new universe
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} className={`p-2 rounded-full transition-colors ${isLight ? 'hover:bg-stone-100 text-stone-400 hover:text-stone-900' : 'hover:bg-stone-800 text-stone-500 hover:text-stone-100'}`}>
                        <X size={20} />
                    </button>
                </div>

                {/* Editor Area */}
                <div className="flex-1 relative">
                    <textarea 
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        placeholder="// Paste your Typescript, Python, Rust, or Go code here...&#10;// The Spectrometer will parse syntax trees into subatomic particles."
                        className={`w-full h-full resize-none p-6 font-mono text-xs sm:text-sm outline-none border-none ${isLight ? 'bg-stone-50 text-stone-800 placeholder:text-stone-400' : 'bg-[#0a0a0a] text-stone-300 placeholder:text-stone-600'}`}
                        spellCheck={false}
                    />
                </div>

                {/* Footer */}
                <div className={`p-4 border-t flex justify-between items-center ${isLight ? 'border-stone-100 bg-white' : 'border-stone-800 bg-stone-900'}`}>
                    <div className={`flex items-center gap-2 text-xs ${isLight ? 'text-stone-500' : 'text-stone-500'}`}>
                        <AlertCircle size={14} />
                        <span>Heuristic parsing active. Results may vary based on syntax.</span>
                    </div>
                    <button 
                        onClick={() => onAnalyze(code)}
                        disabled={!code.trim()}
                        className={`px-6 py-2.5 rounded-lg font-bold text-sm flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${
                            isLight 
                            ? 'bg-stone-900 text-white hover:bg-black shadow-lg shadow-stone-200' 
                            : 'bg-stone-100 text-stone-900 hover:bg-white shadow-lg shadow-black/50'
                        }`}
                    >
                        <Play size={16} fill="currentColor" />
                        Analyze Universe
                    </button>
                </div>
            </div>
        </div>
    );
};
