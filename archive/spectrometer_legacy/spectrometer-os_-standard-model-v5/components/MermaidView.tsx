import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Hadron, Link, Theme, ColorPalette } from '../types';
import { X, ZoomIn, ZoomOut, RefreshCcw, Share2, Filter, PenTool } from 'lucide-react';

interface MermaidViewProps {
    hadrons: Hadron[];
    links: Link[];
    theme: Theme;
    palette: ColorPalette;
    onClose: () => void;
}

export const MermaidView: React.FC<MermaidViewProps> = ({ hadrons, links, theme, palette, onClose }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState(1);
    const [isPanning, setIsPanning] = useState(false);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const lastMousePos = useRef({ x: 0, y: 0 });
    const [isRendering, setIsRendering] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState<string>('All');
    
    // Manual Mode State
    const [showEditor, setShowEditor] = useState(false);
    const [manualCode, setManualCode] = useState('');

    const isLight = theme === 'light';

    const toHex = (num: number) => '#' + num.toString(16).padStart(6, '0');

    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,
            theme: isLight ? 'default' : 'dark',
            securityLevel: 'loose',
            flowchart: {
                curve: 'basis',
                useMaxWidth: false,
                htmlLabels: true,
            }
        });
    }, [theme, isLight]);

    useEffect(() => {
        renderGraph();
    }, [theme, selectedCategory, hadrons, links, manualCode, palette]);

    const renderGraph = async () => {
        setIsRendering(true);
        if (!containerRef.current) return;

        let graphDefinition = '';

        // MODE A: Custom Mermaid Code
        if (manualCode.trim().length > 0) {
            graphDefinition = manualCode;
        } 
        // MODE B: Auto-Generated from Nodes
        else {
            // Filter Logic
            const activeCategories = selectedCategory === 'All' 
                ? ['Data', 'Logic', 'Org', 'Exec'] 
                : [selectedCategory];

            const activeHadrons = hadrons.filter(h => activeCategories.includes(h.cat));
            const activeIds = new Set(activeHadrons.map(h => h.id));
            
            // Filter links: Both source and target must be visible
            const activeLinks = links.filter(l => activeIds.has(l.source) && activeIds.has(l.target));

            graphDefinition = `flowchart TD\n`;

            // 1. Define Styles (Dynamic based on Palette)
            const strokeColor = isLight ? '#333' : '#fff'; // Stronger stroke for nodes
            graphDefinition += `    classDef data fill:${toHex(palette.data)},stroke:${strokeColor},stroke-width:2px,color:#fff;\n`;
            graphDefinition += `    classDef logic fill:${toHex(palette.logic)},stroke:${strokeColor},stroke-width:2px,color:#fff;\n`;
            graphDefinition += `    classDef org fill:${toHex(palette.org)},stroke:${strokeColor},stroke-width:2px,color:#fff;\n`;
            graphDefinition += `    classDef exec fill:${toHex(palette.exec)},stroke:${strokeColor},stroke-width:2px,color:#fff;\n`;

            // Link Style
            const linkColor = isLight ? '#555' : '#aaa';
            graphDefinition += `    linkStyle default stroke:${linkColor},stroke-width:2px,fill:none;\n`;

            // 2. Define Subgraphs (Categories)
            activeCategories.forEach(cat => {
                const catHadrons = activeHadrons.filter(h => h.cat === cat);
                
                if (catHadrons.length > 0) {
                    graphDefinition += `    subgraph ${cat}\n`;
                    graphDefinition += `    direction TB\n`;
                    catHadrons.forEach(h => {
                        // Map shape to mermaid shape
                        let shapeOpen = '[';
                        let shapeClose = ']';
                        if (h.shape === 'sphere') { shapeOpen = '(('; shapeClose = '))'; }
                        else if (h.shape === 'icosahedron') { shapeOpen = '{{'; shapeClose = '}}'; }
                        else if (h.shape === 'torus') { shapeOpen = '(['; shapeClose = '])'; }
                        else if (h.shape === 'octahedron') { shapeOpen = '{'; shapeClose = '}'; }

                        // Sanitize inputs
                        const safeName = h.name.replace(/["<>#]/g, "'");
                        const safeSub = h.sub.replace(/["<>#]/g, "'");

                        const nodeId = `N${h.id}`;
                        graphDefinition += `    ${nodeId}${shapeOpen}"${safeName}<br/><small>${safeSub}</small>"${shapeClose}:::${h.cat.toLowerCase()}\n`;
                    });
                    graphDefinition += `    end\n`;
                }
            });

            // 3. Define Links
            const maxLinks = 2000; 
            const renderLinks = activeLinks.slice(0, maxLinks);
            
            renderLinks.forEach(l => {
                let arrow = '-->';
                let label = '';
                if (l.type === 'Strong') { arrow = '==>'; }
                if (l.type === 'Electromagnetic') { arrow = '-.->'; }
                if (l.type === 'Gravity') { arrow = '---'; }
                if (l.type === 'Entanglement') { arrow = '~~~'; }

                graphDefinition += `    N${l.source} ${arrow} ${label} N${l.target}\n`;
            });

            if (activeHadrons.length === 0) {
                 graphDefinition = `graph TD\nEmptyState["No particles found in ${selectedCategory} sector"]`;
            }
        }

        try {
            // Using a unique ID for the mermaid render to avoid caching conflicts
            const uniqueId = `mermaid-svg-${Date.now()}`;
            // Attempt render
            const { svg } = await mermaid.render(uniqueId, graphDefinition);
            
            if (containerRef.current) {
                containerRef.current.innerHTML = svg;
                
                // CRITICAL: Post-process SVG for visibility
                const svgElement = containerRef.current.querySelector('svg');
                if (svgElement) {
                    // Remove fixed dimensions that cause shrinking
                    svgElement.removeAttribute('height');
                    svgElement.removeAttribute('width');
                    svgElement.style.maxWidth = 'none';
                    svgElement.style.width = '100%';
                    svgElement.style.height = '100%';
                    svgElement.style.overflow = 'visible';
                }
            }
        } catch (error) {
            console.error('Mermaid render failed:', error);
            if (containerRef.current) {
                containerRef.current.innerHTML = `<div class="flex flex-col items-center justify-center h-full text-red-500 font-mono text-sm p-10 text-center gap-2">
                    <span class="font-bold">Rendering Error</span>
                    <span>Syntax invalid or graph too complex.</span>
                </div>`;
            }
        } finally {
            setIsRendering(false);
        }
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        if (e.target instanceof HTMLTextAreaElement) return; // Allow text selection in editor
        setIsPanning(true);
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isPanning) return;
        const dx = e.clientX - lastMousePos.current.x;
        const dy = e.clientY - lastMousePos.current.y;
        setPosition(prev => ({ x: prev.x + dx, y: prev.y + dy }));
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => setIsPanning(false);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 pointer-events-auto">
             <div className={`absolute inset-0 backdrop-blur-md ${isLight ? 'bg-white/80' : 'bg-black/80'}`} onClick={onClose} />
             
             <div className={`relative w-full h-full shadow-2xl rounded-xl border flex flex-col overflow-hidden ${isLight ? 'bg-stone-50 border-stone-200' : 'bg-stone-900 border-stone-800'}`}>
                
                {/* Header */}
                <div className={`p-4 border-b flex flex-wrap justify-between items-center z-10 gap-4 ${isLight ? 'bg-white border-stone-200' : 'bg-stone-950 border-stone-800'}`}>
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isLight ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-900'}`}>
                            <Share2 size={20} />
                        </div>
                        <div>
                            <h2 className={`text-lg font-bold leading-tight ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>Topology Graph</h2>
                            <p className={`text-xs font-mono uppercase tracking-wide ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>
                                {manualCode ? 'Custom Diagram' : 'Force-Directed Relationships'}
                            </p>
                        </div>
                    </div>
                    {/* ... (controls same as before) ... */}
                    <div className="flex items-center gap-2">
                        <button 
                            onClick={() => setShowEditor(!showEditor)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold uppercase tracking-wider transition-all ${
                                showEditor 
                                ? (isLight ? 'bg-stone-900 text-white border-stone-900' : 'bg-stone-100 text-stone-900 border-stone-100')
                                : (isLight ? 'bg-white text-stone-600 border-stone-200 hover:bg-stone-50' : 'bg-stone-800 text-stone-300 border-stone-700 hover:bg-stone-700')
                            }`}
                        >
                            <PenTool size={12} />
                            {showEditor ? 'Close Editor' : 'Edit Graph'}
                        </button>
                        <div className="w-px h-6 bg-stone-300 mx-1"></div>
                        {!manualCode && (
                            <div className={`hidden sm:flex items-center border rounded-lg p-1 mr-2 ${isLight ? 'bg-stone-100 border-stone-200' : 'bg-stone-800 border-stone-700'}`}>
                                <Filter size={14} className={`ml-2 mr-1 ${isLight ? 'text-stone-400' : 'text-stone-500'}`} />
                                <select 
                                    value={selectedCategory} 
                                    onChange={(e) => { setSelectedCategory(e.target.value); setScale(1); setPosition({x:0,y:0}); }}
                                    className={`bg-transparent text-xs font-medium outline-none p-1 cursor-pointer ${isLight ? 'text-stone-600' : 'text-stone-300'}`}
                                >
                                    <option value="All">All Layers</option>
                                    <option value="Data">Data</option>
                                    <option value="Logic">Logic</option>
                                    <option value="Org">Org</option>
                                    <option value="Exec">Exec</option>
                                </select>
                            </div>
                        )}
                        <div className={`flex items-center border rounded-lg p-1 ${isLight ? 'bg-stone-100 border-stone-200' : 'bg-stone-800 border-stone-700'}`}>
                             <button onClick={() => setScale(s => Math.max(0.2, s - 0.2))} className={`p-2 rounded hover:bg-black/10 transition ${isLight ? 'text-stone-600' : 'text-stone-300'}`}><ZoomOut size={16}/></button>
                             <span className={`text-xs font-mono w-12 text-center ${isLight ? 'text-stone-600' : 'text-stone-300'}`}>{Math.round(scale * 100)}%</span>
                             <button onClick={() => setScale(s => Math.min(3, s + 0.2))} className={`p-2 rounded hover:bg-black/10 transition ${isLight ? 'text-stone-600' : 'text-stone-300'}`}><ZoomIn size={16}/></button>
                             <div className="w-px h-4 bg-stone-300 mx-1"></div>
                             <button onClick={() => { setScale(1); setPosition({x:0,y:0}); }} className={`p-2 rounded hover:bg-black/10 transition ${isLight ? 'text-stone-600' : 'text-stone-300'}`}><RefreshCcw size={16}/></button>
                        </div>
                        <button onClick={onClose} className={`p-2 rounded-full hover:bg-black/10 transition ${isLight ? 'text-stone-600' : 'text-stone-300'}`}>
                            <X size={24} />
                        </button>
                    </div>
                </div>

                {/* Editor Overlay and Canvas same as before */}
                {showEditor && (
                    <div className={`absolute top-[72px] right-0 bottom-0 w-80 md:w-96 z-30 border-l flex flex-col transition-transform duration-300 ${isLight ? 'bg-white border-stone-200' : 'bg-stone-950 border-stone-800'}`}>
                        <div className={`p-3 border-b text-xs font-bold uppercase tracking-wider flex justify-between items-center ${isLight ? 'bg-stone-50 border-stone-100 text-stone-600' : 'bg-stone-900 border-stone-800 text-stone-400'}`}>
                            <span>Mermaid Syntax</span>
                            {manualCode && (
                                <button onClick={() => setManualCode('')} className="text-[10px] text-red-500 hover:underline">Clear & Reset</button>
                            )}
                        </div>
                        <textarea
                            value={manualCode}
                            onChange={(e) => setManualCode(e.target.value)}
                            placeholder={`graph TD;\n  A[Client] --> B{Load Balancer};\n  B --> C[Server 1];\n  B --> D[Server 2];`}
                            className={`flex-1 resize-none p-4 font-mono text-xs outline-none ${isLight ? 'bg-white text-stone-800' : 'bg-[#0a0a0a] text-stone-300'}`}
                            spellCheck={false}
                        />
                        <div className={`p-3 border-t text-[10px] text-stone-500 ${isLight ? 'bg-stone-50 border-stone-100' : 'bg-stone-900 border-stone-800'}`}>
                            {manualCode ? 'Rendering Custom Code' : 'Rendering System Topology (Default)'}
                        </div>
                    </div>
                )}

                <div 
                    className="flex-1 overflow-hidden relative cursor-move bg-opacity-50"
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                    style={{
                        backgroundImage: `radial-gradient(${isLight ? '#ddd' : '#333'} 1px, transparent 1px)`,
                        backgroundSize: '20px 20px'
                    }}
                >
                    {isRendering && (
                        <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
                             <div className={`flex flex-col items-center gap-3 ${isLight ? 'text-stone-400' : 'text-stone-500'}`}>
                                <RefreshCcw className="animate-spin" size={32} />
                                <span className="text-xs font-mono uppercase tracking-widest">Processing Graph...</span>
                             </div>
                        </div>
                    )}
                    
                    <div 
                        ref={containerRef}
                        className={`transition-opacity duration-200 origin-center ${isRendering ? 'opacity-0' : 'opacity-100'}`}
                        style={{
                            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`
                        }}
                    />
                </div>
             </div>
        </div>
    );
};