import React, { useState, useEffect } from 'react';
import { LabScene } from './components/LabScene';
import { StandardModelTable } from './components/StandardModelTable';
import { MermaidView } from './components/MermaidView';
import { CodeInput } from './components/CodeInput';
import { generateHadrons, generateLinks, PHYSICS_DEFAULTS, PALETTES, recolorHadrons } from './data';
import { PhysicsSettings, Theme, Hadron, Link } from './types';
import { Atom, Settings2, Sliders, X, Zap, Activity, Info, BookOpen, Waves, Sun, Moon, Share2, FileCode, Palette, Orbit } from 'lucide-react';

export default function App() {
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [settings, setSettings] = useState<PhysicsSettings>(PHYSICS_DEFAULTS);
    const [theme, setTheme] = useState<Theme>('light');
    const [showSettings, setShowSettings] = useState(false);
    const [showTable, setShowTable] = useState(false);
    const [showGraph, setShowGraph] = useState(false);
    const [showCode, setShowCode] = useState(false);
    
    // Palette State
    const [paletteName, setPaletteName] = useState('Standard');
    const currentPalette = PALETTES[paletteName] || PALETTES['Standard'];

    // State for Simulation Data - Initialize Immediately with default palette
    const [hadrons, setHadrons] = useState<Hadron[]>(() => generateHadrons(undefined, currentPalette));
    const [links, setLinks] = useState<Link[]>(() => generateLinks(hadrons)); // Init with same particles

    // Recolor hadrons whenever palette changes
    useEffect(() => {
        setHadrons(prev => recolorHadrons(prev, currentPalette));
    }, [paletteName]);

    // We ensure links are synced if hadrons changed significantly (e.g. Code Input)
    const handleAnalyzeCode = (code: string) => {
        const newHadrons = generateHadrons(code, currentPalette);
        const newLinks = generateLinks(newHadrons, code);
        setHadrons(newHadrons);
        setLinks(newLinks);
        setShowCode(false);
        setSelectedId(null);
    };

    const selectedHadron = hadrons.find(h => h.id === selectedId);
    const isLight = theme === 'light';

    const SliderControl = ({ label, value, min, max, step, onChange }: any) => (
        <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
                <label className={`text-[10px] uppercase font-bold tracking-wider ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>{label}</label>
                <span className={`text-[10px] font-mono ${isLight ? 'text-stone-400' : 'text-stone-500'}`}>{value.toFixed(3)}</span>
            </div>
            <input 
                type="range" min={min} max={max} step={step} value={value} 
                onChange={(e) => onChange(parseFloat(e.target.value))} 
            />
        </div>
    );

    return (
        <div className={`relative w-full h-full font-sans overflow-hidden select-none transition-colors duration-500 ${isLight ? 'bg-white text-stone-900' : 'bg-[#050505] text-stone-100'}`}>
            
            <LabScene 
                hadrons={hadrons}
                links={links}
                settings={settings}
                selectedId={selectedId}
                theme={theme}
                palette={currentPalette}
                onSelect={setSelectedId}
                onKick={() => {}} 
            />

            {/* Top HUD */}
            <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start pointer-events-none z-10">
                <div className={`${isLight ? 'bg-white/80 border-stone-200' : 'bg-stone-900/80 border-stone-800'} backdrop-blur-md shadow-lg rounded-lg border p-4 flex items-center gap-3 transition-colors`}>
                    <div className="w-8 h-8 bg-black rounded-md flex items-center justify-center text-white shadow-md">
                        <Atom size={18} />
                    </div>
                    <div>
                        <h1 className={`text-sm font-bold tracking-tight ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>Spectrometer OS</h1>
                        <p className={`text-[10px] font-mono uppercase tracking-wider ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>Standard Model v6.1 (Unified)</p>
                    </div>
                </div>

                <div className="flex gap-2 pointer-events-auto">
                    <button 
                        onClick={() => setTheme(prev => prev === 'light' ? 'dark' : 'light')}
                        className={`${isLight ? 'bg-white border-stone-200 text-stone-600 hover:bg-stone-50' : 'bg-stone-900 border-stone-800 text-stone-400 hover:bg-stone-800'} shadow-md rounded-full border w-10 h-10 flex items-center justify-center transition-all active:scale-95`}
                        title="Toggle Theme"
                    >
                        {isLight ? <Moon size={18} /> : <Sun size={18} />}
                    </button>
                    <button 
                        onClick={() => { setShowCode(true); setShowTable(false); setShowGraph(false); setShowSettings(false); }}
                        className={`${isLight ? 'bg-white border-stone-200 text-stone-600 hover:bg-stone-50' : 'bg-stone-900 border-stone-800 text-stone-400 hover:bg-stone-800'} shadow-md rounded-full border w-10 h-10 flex items-center justify-center transition-all active:scale-95 group`}
                        title="Inject Source Code"
                    >
                        <FileCode size={18} className="group-hover:text-green-500 transition-colors" />
                    </button>
                    <button 
                        onClick={() => { setShowGraph(true); setShowTable(false); setShowCode(false); setShowSettings(false); }}
                        className={`${isLight ? 'bg-white border-stone-200 text-stone-600 hover:bg-stone-50' : 'bg-stone-900 border-stone-800 text-stone-400 hover:bg-stone-800'} shadow-md rounded-full border w-10 h-10 flex items-center justify-center transition-all active:scale-95 group`}
                        title="Topology Graph (Mermaid)"
                    >
                        <Share2 size={18} className="group-hover:text-purple-500 transition-colors" />
                    </button>
                    <button 
                        onClick={() => { setShowTable(true); setShowGraph(false); setShowCode(false); setShowSettings(false); }}
                        className={`${isLight ? 'bg-white border-stone-200 text-stone-600 hover:bg-stone-50' : 'bg-stone-900 border-stone-800 text-stone-400 hover:bg-stone-800'} shadow-md rounded-full border w-10 h-10 flex items-center justify-center transition-all active:scale-95 group`}
                        title="Standard Model Table"
                    >
                        <BookOpen size={18} className="group-hover:text-blue-500 transition-colors" />
                    </button>
                    <button 
                        onClick={() => setShowSettings(!showSettings)}
                        className={`${isLight ? 'bg-white border-stone-200 text-stone-600 hover:bg-stone-50' : 'bg-stone-900 border-stone-800 text-stone-400 hover:bg-stone-800'} shadow-md rounded-full border w-10 h-10 flex items-center justify-center transition-all active:scale-95 ${showSettings ? (isLight ? 'bg-stone-100 ring-2 ring-stone-200' : 'bg-stone-800 ring-2 ring-stone-700') : ''}`}
                        title="Settings"
                    >
                        {showSettings ? <X size={18} /> : <Settings2 size={18} />}
                    </button>
                </div>
            </div>

            {/* CODE INPUT MODAL */}
            {showCode && (
                <CodeInput 
                    theme={theme}
                    onClose={() => setShowCode(false)}
                    onAnalyze={handleAnalyzeCode}
                />
            )}

            {/* MERMAID GRAPH MODAL */}
            {showGraph && (
                <MermaidView 
                    hadrons={hadrons} 
                    links={links}
                    theme={theme}
                    palette={currentPalette}
                    onClose={() => setShowGraph(false)}
                />
            )}

            {/* TABLE MODAL */}
            {showTable && (
                <StandardModelTable 
                    hadrons={hadrons} 
                    theme={theme}
                    palette={currentPalette}
                    onClose={() => setShowTable(false)}
                    onSelect={(id) => setSelectedId(id)}
                />
            )}

            {/* SETTINGS PANEL */}
            {showSettings && (
                <div className="absolute top-24 right-6 w-72 pointer-events-auto z-30 ui-panel-enter-active">
                    <div className={`${isLight ? 'bg-white/95 border-stone-200' : 'bg-stone-900/95 border-stone-800'} backdrop-blur-xl shadow-2xl rounded-xl border overflow-hidden`}>
                        <div className={`p-4 border-b flex items-center gap-2 ${isLight ? 'border-stone-100 bg-stone-50/50' : 'border-stone-800 bg-stone-950/50'}`}>
                            <Sliders size={14} className="text-stone-500" />
                            <h3 className={`text-xs font-bold uppercase tracking-wide ${isLight ? 'text-stone-700' : 'text-stone-300'}`}>Universe Console</h3>
                        </div>
                        <div className="p-5 max-h-[70vh] overflow-y-auto custom-scrollbar">
                            
                            <div className="mb-6">
                                <h4 className={`text-xs font-semibold mb-3 flex items-center gap-2 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>
                                    <Palette size={12} className="text-pink-500" /> Color Palette
                                </h4>
                                <div className="grid grid-cols-2 gap-2">
                                    {Object.keys(PALETTES).map(pName => (
                                        <button 
                                            key={pName}
                                            onClick={() => setPaletteName(pName)}
                                            className={`text-[10px] font-bold uppercase p-2 rounded border transition-all flex items-center gap-2 ${
                                                paletteName === pName 
                                                ? (isLight ? 'bg-stone-900 text-white border-stone-900' : 'bg-stone-100 text-stone-900 border-stone-100')
                                                : (isLight ? 'bg-white hover:bg-stone-50 text-stone-500 border-stone-200' : 'bg-stone-950 hover:bg-stone-900 text-stone-400 border-stone-800')
                                            }`}
                                        >
                                            <div className="flex gap-0.5">
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#' + PALETTES[pName].data.toString(16).padStart(6, '0') }}></div>
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#' + PALETTES[pName].logic.toString(16).padStart(6, '0') }}></div>
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#' + PALETTES[pName].org.toString(16).padStart(6, '0') }}></div>
                                            </div>
                                            {pName}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className={`pt-4 border-t mb-6 ${isLight ? 'border-stone-100' : 'border-stone-800'}`}>
                                <h4 className={`text-xs font-semibold mb-3 flex items-center gap-2 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>
                                    <Activity size={12} className="text-blue-500" /> Environment
                                </h4>
                                <SliderControl label="Entropy (Brownian)" value={settings.brownianStrength} min={0} max={0.2} step={0.001} onChange={(v:number) => setSettings(s => ({...s, brownianStrength: v}))} />
                                <SliderControl label="Viscosity (Drag)" value={settings.drag} min={0.90} max={0.999} step={0.001} onChange={(v:number) => setSettings(s => ({...s, drag: v}))} />
                                <SliderControl label="Global Gravity" value={settings.gravity} min={-1.0} max={1.0} step={0.01} onChange={(v:number) => setSettings(s => ({...s, gravity: v}))} />
                                <SliderControl label="Layer Attraction" value={settings.layerPull} min={0} max={0.01} step={0.0001} onChange={(v:number) => setSettings(s => ({...s, layerPull: v}))} />
                            </div>

                            <div className={`pt-4 border-t mb-6 ${isLight ? 'border-stone-100' : 'border-stone-800'}`}>
                                <h4 className={`text-xs font-semibold mb-3 flex items-center gap-2 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>
                                    <Orbit size={12} className="text-teal-500" /> Exotic Physics
                                </h4>
                                <SliderControl label="Dark Energy (Expansion)" value={settings.darkEnergy} min={0} max={1.0} step={0.01} onChange={(v:number) => setSettings(s => ({...s, darkEnergy: v}))} />
                                <SliderControl label="Lattice Field (Order)" value={settings.latticeStrength} min={0} max={0.2} step={0.01} onChange={(v:number) => setSettings(s => ({...s, latticeStrength: v}))} />
                                <SliderControl label="Quantum Flux (Time)" value={settings.quantumFlux} min={0} max={1.0} step={0.01} onChange={(v:number) => setSettings(s => ({...s, quantumFlux: v}))} />
                            </div>

                            <div className={`pt-4 border-t mb-6 ${isLight ? 'border-stone-100' : 'border-stone-800'}`}>
                                <h4 className={`text-xs font-semibold mb-3 flex items-center gap-2 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>
                                    <Waves size={12} className="text-purple-500" /> Fields & Forces
                                </h4>
                                
                                <div className={`flex items-center justify-between mb-3 p-2 rounded border ${isLight ? 'bg-stone-50 border-stone-100' : 'bg-stone-950 border-stone-800'}`}>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-stone-400"></div>
                                        <label className={`text-[10px] uppercase font-bold tracking-wider ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>Higgs Field</label>
                                    </div>
                                    <input type="checkbox" checked={settings.higgsField} onChange={(e) => setSettings(s => ({...s, higgsField: e.target.checked}))} className="accent-black w-4 h-4" />
                                </div>

                                <div className={`flex items-center justify-between mb-3 p-2 rounded border ${isLight ? 'bg-stone-50 border-stone-100' : 'bg-stone-950 border-stone-800'}`}>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                        <label className={`text-[10px] uppercase font-bold tracking-wider ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>Fundamental Forces</label>
                                    </div>
                                    <input type="checkbox" checked={settings.showForces} onChange={(e) => setSettings(s => ({...s, showForces: e.target.checked}))} className="accent-black w-4 h-4" />
                                </div>
                            </div>

                            <div className={`pt-4 border-t ${isLight ? 'border-stone-100' : 'border-stone-800'}`}>
                                <h4 className={`text-xs font-semibold mb-3 flex items-center gap-2 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>
                                    <Zap size={12} className="text-amber-500" /> Interaction
                                </h4>
                                <SliderControl label="Kick Force" value={settings.kickStrength} min={10} max={300} step={5} onChange={(v:number) => setSettings(s => ({...s, kickStrength: v}))} />
                                <SliderControl label="Blast Radius" value={settings.blastRadius} min={50} max={400} step={10} onChange={(v:number) => setSettings(s => ({...s, blastRadius: v}))} />
                            </div>

                            <div className={`mt-6 pt-4 border-t flex justify-end ${isLight ? 'border-stone-100' : 'border-stone-800'}`}>
                                <button 
                                    onClick={() => {
                                        setSettings(PHYSICS_DEFAULTS);
                                        const defHadrons = generateHadrons();
                                        setHadrons(defHadrons);
                                        setLinks(generateLinks(defHadrons));
                                    }}
                                    className="text-[10px] font-medium text-stone-400 hover:text-red-500 transition-colors"
                                >
                                    Reset Universe
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* DETAIL PANEL */}
            {selectedHadron && !showSettings && !showTable && !showGraph && !showCode && (
                <div className="absolute top-24 right-6 w-80 pointer-events-none z-20 ui-panel-enter-active">
                    <div className={`${isLight ? 'bg-white/95 border-stone-200' : 'bg-stone-900/95 border-stone-800'} backdrop-blur-xl shadow-2xl rounded-xl border overflow-hidden pointer-events-auto`}>
                        <div className={`p-4 border-b flex justify-between items-start ${isLight ? 'border-stone-100 bg-stone-50/50' : 'border-stone-800 bg-stone-950/50'}`}>
                            <div className="flex items-center gap-3">
                                <div 
                                    className="w-3 h-3 rounded-full shadow-sm" 
                                    style={{ backgroundColor: '#' + selectedHadron.color.toString(16).padStart(6, '0') }} 
                                />
                                <div>
                                    <div className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                                        {selectedHadron.cat} / {selectedHadron.sub}
                                    </div>
                                    <h2 className={`text-lg font-semibold leading-tight ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>{selectedHadron.name}</h2>
                                </div>
                            </div>
                            <button onClick={() => setSelectedId(null)} className={`hover:${isLight ? 'bg-stone-100' : 'bg-stone-800'} rounded p-1 transition-colors`}>
                                <X size={18} className="text-stone-400" />
                            </button>
                        </div>
                        
                        <div className="p-5 grid grid-cols-2 gap-3">
                            <div className={`p-2 rounded border transition-colors ${isLight ? 'bg-stone-50 border-stone-100 hover:border-stone-200' : 'bg-stone-950 border-stone-800 hover:border-stone-700'}`}>
                                <div className="text-[10px] uppercase text-stone-400 font-bold mb-1 flex items-center gap-1">
                                    <Zap size={10} /> Charge
                                </div>
                                <div className={`text-sm font-mono font-medium ${isLight ? 'text-stone-800' : 'text-stone-200'}`}>{selectedHadron.boundary}</div>
                            </div>
                            <div className={`p-2 rounded border transition-colors ${isLight ? 'bg-stone-50 border-stone-100 hover:border-stone-200' : 'bg-stone-950 border-stone-800 hover:border-stone-700'}`}>
                                <div className="text-[10px] uppercase text-stone-400 font-bold mb-1 flex items-center gap-1">
                                    <Activity size={10} /> Spin
                                </div>
                                <div className={`text-sm font-mono font-medium ${isLight ? 'text-stone-800' : 'text-stone-200'}`}>{selectedHadron.activation}</div>
                            </div>
                            <div className={`p-2 rounded border transition-colors ${isLight ? 'bg-stone-50 border-stone-100 hover:border-stone-200' : 'bg-stone-950 border-stone-800 hover:border-stone-700'}`}>
                                <div className="text-[10px] uppercase text-stone-400 font-bold mb-1">Mass</div>
                                <div className={`text-sm font-mono font-medium ${isLight ? 'text-stone-800' : 'text-stone-200'}`}>{selectedHadron.lifetime}</div>
                            </div>
                            <div className={`p-2 rounded border transition-colors ${isLight ? 'bg-stone-50 border-stone-100 hover:border-stone-200' : 'bg-stone-950 border-stone-800 hover:border-stone-700'}`}>
                                <div className="text-[10px] uppercase text-stone-400 font-bold mb-1">Decay</div>
                                <div className={`text-sm font-mono font-medium ${isLight ? 'text-stone-800' : 'text-stone-200'}`}>{selectedHadron.state}</div>
                            </div>
                            <div className={`p-2 rounded border col-span-2 transition-colors ${isLight ? 'bg-stone-50 border-stone-100 hover:border-stone-200' : 'bg-stone-950 border-stone-800 hover:border-stone-700'}`}>
                                <div className="text-[10px] uppercase text-stone-400 font-bold mb-1">Generation</div>
                                <div className={`text-sm font-mono font-medium ${isLight ? 'text-stone-800' : 'text-stone-200'}`}>{selectedHadron.layer} Layer</div>
                            </div>
                        </div>
                        
                        <div className="px-5 pb-5">
                            <div className={`${isLight ? 'bg-blue-50/50 border-blue-100' : 'bg-blue-900/20 border-blue-900/30'} p-3 rounded-md border`}>
                                <p className={`text-xs leading-relaxed italic flex gap-2 ${isLight ? 'text-stone-600' : 'text-stone-400'}`}>
                                    <Info size={14} className="text-blue-400 shrink-0 mt-0.5" />
                                    {selectedHadron.desc}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Instruction Toast */}
            {!selectedHadron && !showSettings && !showTable && !showGraph && !showCode && (
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 pointer-events-none opacity-50 animate-pulse">
                    <p className={`text-[10px] uppercase tracking-widest font-medium px-3 py-1 rounded-full backdrop-blur-sm ${isLight ? 'text-stone-400 bg-white/50' : 'text-stone-500 bg-black/50'}`}>
                        Double Click to Kick Particles
                    </p>
                </div>
            )}
        </div>
    );
}