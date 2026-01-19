import React, { useState, useMemo } from 'react';
import { Hadron, Theme, ColorPalette } from '../types';
import { X, Search, ArrowUpDown, Filter, Atom, Zap, Activity, Database, LayoutGrid, List } from 'lucide-react';

interface StandardModelTableProps {
    hadrons: Hadron[];
    theme: Theme;
    palette: ColorPalette;
    onClose: () => void;
    onSelect: (id: number) => void;
}

type SortField = 'id' | 'name' | 'cat' | 'mass' | 'charge' | 'spin';
type ViewMode = 'list' | 'grid';

const toHex = (num: number) => '#' + num.toString(16).padStart(6, '0');

const ParticleIcon = ({ hadron, palette }: { hadron: Hadron, palette: ColorPalette }) => {
    // Use hadron color (which is updated via prop) or fallback
    const color = toHex(hadron.color);
    
    // Boundary/Charge Colors from Palette
    let glowColor = 'transparent';
    if (hadron.boundary === 'In') glowColor = toHex(palette.chargeIn);
    if (hadron.boundary === 'Out') glowColor = toHex(palette.chargeOut);
    if (hadron.boundary === 'In&Out') glowColor = toHex(palette.chargeMix);

    // Shape rendering (Simplified SVG representations of 3D geometry)
    const renderShape = () => {
        const commonProps = { fill: color, stroke: 'rgba(0,0,0,0.1)', strokeWidth: 1 };
        
        switch (hadron.shape) {
            case 'tetrahedron': // Triangle
                return <polygon points="16,4 28,26 4,26" {...commonProps} />;
            case 'cube': // Square
                return <rect x="6" y="6" width="20" height="20" rx="2" {...commonProps} />;
            case 'sphere': // Circle
                return <circle cx="16" cy="16" r="11" {...commonProps} />;
            case 'icosahedron': // Hexagon-ish
                return <polygon points="16,2 29,9 29,23 16,30 3,23 3,9" {...commonProps} />;
            case 'octahedron': // Diamond
                return <polygon points="16,2 28,16 16,30 4,16" {...commonProps} />;
            case 'dodecahedron': // Pentagon
                return <polygon points="16,2 30,12 25,29 7,29 2,12" {...commonProps} />;
            case 'cone': // Triangle tall
                return <polygon points="16,2 26,28 6,28" {...commonProps} />;
            case 'cylinder': // Rect tall
                return <rect x="8" y="4" width="16" height="24" rx="4" {...commonProps} />;
            case 'torus': // Donut
                return (
                    <g>
                        <circle cx="16" cy="16" r="12" {...commonProps} fill="none" stroke={color} strokeWidth="6" />
                    </g>
                );
            default:
                return <circle cx="16" cy="16" r="10" {...commonProps} />;
        }
    };

    return (
        <div className="relative w-12 h-12 flex items-center justify-center">
            {/* Charge Halo */}
            {hadron.boundary !== 'Internal' && (
                <div 
                    className="absolute inset-0 rounded-full blur-md opacity-60"
                    style={{ backgroundColor: glowColor, transform: 'scale(0.8)' }}
                />
            )}
            
            {/* Shape SVG */}
            <svg width="32" height="32" viewBox="0 0 32 32" className="drop-shadow-sm relative z-10 overflow-visible">
                <defs>
                    <linearGradient id={`grad-${hadron.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="white" stopOpacity="0.5" />
                        <stop offset="100%" stopColor="black" stopOpacity="0.1" />
                    </linearGradient>
                </defs>
                {renderShape()}
                {/* Gloss overlay */}
                {renderShape && React.cloneElement(renderShape(), { fill: `url(#grad-${hadron.id})`, stroke: 'none', style: { mixBlendMode: 'overlay' } } as any)}
            </svg>
            
            {/* Animation state indicator */}
            {hadron.state === 'Stateless' && (
                <div className="absolute top-0 right-0 w-2 h-2 bg-white rounded-full animate-pulse shadow-sm border border-stone-200" />
            )}
        </div>
    );
};

export const StandardModelTable: React.FC<StandardModelTableProps> = ({ hadrons, theme, palette, onClose, onSelect }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortField, setSortField] = useState<SortField>('id');
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
    const [filterCat, setFilterCat] = useState<string>('All');
    const [viewMode, setViewMode] = useState<ViewMode>('list');

    const isLight = theme === 'light';

    // ... (Sort/Filter logic remains the same) ...
    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('asc');
        }
    };

    const filteredAndSortedHadrons = useMemo(() => {
        let result = [...hadrons];
        if (filterCat !== 'All') {
            result = result.filter(h => h.cat === filterCat);
        }
        if (searchTerm) {
            const lower = searchTerm.toLowerCase();
            result = result.filter(h => 
                h.name.toLowerCase().includes(lower) || 
                h.sub.toLowerCase().includes(lower) ||
                h.desc.toLowerCase().includes(lower)
            );
        }
        result.sort((a, b) => {
            let valA: any = a[sortField as keyof Hadron];
            let valB: any = b[sortField as keyof Hadron];
            if (sortField === 'mass') { valA = a.lifetime; valB = b.lifetime; }
            if (sortField === 'charge') { valA = a.boundary; valB = b.boundary; }
            if (sortField === 'spin') { valA = a.activation; valB = b.activation; }
            if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
        return result;
    }, [hadrons, searchTerm, sortField, sortDirection, filterCat]);

    const categories = ['All', 'Data', 'Logic', 'Org', 'Exec'];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-10 pointer-events-auto">
            <div className={`absolute inset-0 backdrop-blur-md ${isLight ? 'bg-white/60' : 'bg-black/60'}`} onClick={onClose} />
            
            <div className={`relative w-full max-w-6xl h-full max-h-[90vh] shadow-2xl rounded-xl border flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200 ${isLight ? 'bg-white border-stone-200' : 'bg-stone-900 border-stone-800'}`}>
                
                {/* Header */}
                <div className={`p-5 border-b flex justify-between items-center ${isLight ? 'border-stone-100 bg-stone-50/50' : 'border-stone-800 bg-stone-950/50'}`}>
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isLight ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-900'}`}>
                            <Database size={20} />
                        </div>
                        <div>
                            <h2 className={`text-lg font-bold leading-tight ${isLight ? 'text-stone-900' : 'text-stone-100'}`}>Standard Model Table</h2>
                            <p className={`text-xs font-mono uppercase tracking-wide ${isLight ? 'text-stone-500' : 'text-stone-400'}`}>
                                {filteredAndSortedHadrons.length} Particles Detected
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className={`border rounded-lg p-1 flex gap-1 shadow-sm ${isLight ? 'bg-white border-stone-200' : 'bg-stone-800 border-stone-700'}`}>
                            <button 
                                onClick={() => setViewMode('list')}
                                className={`p-1.5 rounded-md transition-all ${viewMode === 'list' ? (isLight ? 'bg-stone-100 text-stone-900' : 'bg-stone-700 text-stone-100') : 'text-stone-400 hover:text-stone-500'}`}
                                title="List View"
                            >
                                <List size={18} />
                            </button>
                            <button 
                                onClick={() => setViewMode('grid')}
                                className={`p-1.5 rounded-md transition-all ${viewMode === 'grid' ? (isLight ? 'bg-stone-100 text-stone-900' : 'bg-stone-700 text-stone-100') : 'text-stone-400 hover:text-stone-500'}`}
                                title="Periodic Grid View"
                            >
                                <LayoutGrid size={18} />
                            </button>
                        </div>
                        <button onClick={onClose} className={`p-2 rounded-full transition-colors ${isLight ? 'hover:bg-stone-100 text-stone-400 hover:text-stone-900' : 'hover:bg-stone-800 text-stone-500 hover:text-stone-100'}`}>
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Toolbar */}
                <div className={`p-4 border-b flex flex-wrap gap-4 items-center justify-between ${isLight ? 'border-stone-100 bg-white' : 'border-stone-800 bg-stone-900'}`}>
                    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border w-full sm:w-auto min-w-[300px] ${isLight ? 'bg-stone-50 border-stone-200' : 'bg-stone-950 border-stone-800'}`}>
                        <Search size={16} className="text-stone-400" />
                        <input 
                            type="text" 
                            placeholder="Search by name, type, or description..." 
                            className={`bg-transparent border-none outline-none text-sm w-full placeholder:text-stone-400 ${isLight ? 'text-stone-900' : 'text-stone-100'}`}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <div className="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
                        {categories.map(cat => (
                            <button
                                key={cat}
                                onClick={() => setFilterCat(cat)}
                                className={`px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider transition-all border ${
                                    filterCat === cat 
                                    ? (isLight ? 'bg-stone-900 text-white border-stone-900' : 'bg-stone-100 text-stone-900 border-stone-100')
                                    : (isLight ? 'bg-white text-stone-500 border-stone-200 hover:border-stone-300' : 'bg-stone-900 text-stone-400 border-stone-800 hover:border-stone-700')
                                }`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className={`flex-1 overflow-auto custom-scrollbar ${isLight ? 'bg-white' : 'bg-stone-900'}`}>
                    {viewMode === 'list' ? (
                        <table className="w-full min-w-[700px] text-left border-collapse">
                            <thead className={`sticky top-0 z-40 shadow-sm ${isLight ? 'bg-stone-50' : 'bg-stone-950'}`}>
                                <tr>
                                    <th onClick={() => handleSort('id')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors w-16">
                                        <div className="flex items-center gap-1">ID <ArrowUpDown size={10} /></div>
                                    </th>
                                    <th onClick={() => handleSort('cat')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors w-24">
                                        <div className="flex items-center gap-1">Quark <ArrowUpDown size={10} /></div>
                                    </th>
                                    <th onClick={() => handleSort('name')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors">
                                        <div className="flex items-center gap-1">Hádron <ArrowUpDown size={10} /></div>
                                    </th>
                                    <th onClick={() => handleSort('charge')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors w-32">
                                        <div className="flex items-center gap-1">Charge <Zap size={10} /></div>
                                    </th>
                                    <th onClick={() => handleSort('mass')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors w-32">
                                        <div className="flex items-center gap-1">Mass <Atom size={10} /></div>
                                    </th>
                                    <th onClick={() => handleSort('spin')} className="p-4 text-[10px] font-bold text-stone-500 uppercase tracking-wider cursor-pointer hover:bg-opacity-80 transition-colors w-32">
                                        <div className="flex items-center gap-1">Spin <Activity size={10} /></div>
                                    </th>
                                </tr>
                            </thead>
                            <tbody className={`divide-y ${isLight ? 'divide-stone-100' : 'divide-stone-800'}`}>
                                {filteredAndSortedHadrons.map((h) => (
                                    <tr 
                                        key={h.id} 
                                        onClick={() => { onSelect(h.id); onClose(); }}
                                        className={`cursor-pointer transition-colors group ${isLight ? 'hover:bg-blue-50/50' : 'hover:bg-blue-900/10'}`}
                                    >
                                        <td className="p-4 text-xs font-mono text-stone-400">
                                            {h.id.toString().padStart(3, '0')}
                                        </td>
                                        <td className="p-4">
                                            <span 
                                                className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border opacity-80"
                                                style={{ 
                                                    borderColor: toHex(h.color), 
                                                    color: toHex(h.color),
                                                    backgroundColor: toHex(h.color) + '15'
                                                }}
                                            >
                                                {h.cat}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 flex-shrink-0">
                                                    <ParticleIcon hadron={h} palette={palette} />
                                                </div>
                                                <div>
                                                    <div className={`font-semibold text-sm group-hover:text-blue-500 transition-colors ${isLight ? 'text-stone-900' : 'text-stone-200'}`}>
                                                        {h.name}
                                                    </div>
                                                    <div className="text-xs text-stone-500 mt-0.5 font-light">
                                                        {h.desc}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4 text-xs font-mono text-stone-500">
                                            {h.boundary}
                                        </td>
                                        <td className="p-4 text-xs font-mono text-stone-500">
                                            {h.lifetime}
                                        </td>
                                        <td className="p-4 text-xs font-mono text-stone-500">
                                            {h.activation}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="p-6">
                            {['Data', 'Logic', 'Org', 'Exec'].map((cat) => {
                                const catHadrons = filteredAndSortedHadrons.filter(h => h.cat === cat);
                                if (catHadrons.length === 0) return null;
                                
                                // Dynamic category color
                                let catColor = palette.data;
                                if (cat === 'Logic') catColor = palette.logic;
                                if (cat === 'Org') catColor = palette.org;
                                if (cat === 'Exec') catColor = palette.exec;

                                return (
                                    <div key={cat} className="mb-8">
                                        <h3 
                                            className="text-sm font-bold uppercase tracking-widest mb-4 flex items-center gap-2"
                                            style={{ color: toHex(catColor) }}
                                        >
                                            <span className="w-2 h-2 rounded-full bg-current" />
                                            {cat} Particles
                                        </h3>
                                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                                            {catHadrons.map(h => (
                                                <div 
                                                    key={h.id}
                                                    onClick={() => { onSelect(h.id); onClose(); }}
                                                    className={`group relative border rounded-xl p-3 cursor-pointer transition-all duration-200 flex flex-col items-center text-center h-32 justify-between ${
                                                        isLight 
                                                        ? 'bg-stone-50 hover:bg-white border-stone-200 hover:border-blue-300 hover:shadow-lg' 
                                                        : 'bg-stone-950 hover:bg-stone-900 border-stone-800 hover:border-blue-700 hover:shadow-lg hover:shadow-blue-900/20'
                                                    }`}
                                                >
                                                    <div className="absolute top-2 left-2 text-[10px] font-mono text-stone-500 opacity-50">
                                                        {h.id.toString().padStart(2, '0')}
                                                    </div>
                                                    <div className="flex-1 flex items-center justify-center w-full mt-2">
                                                        <div className="transform group-hover:scale-110 transition-transform duration-300">
                                                            <ParticleIcon hadron={h} palette={palette} />
                                                        </div>
                                                    </div>
                                                    <div className="w-full">
                                                        <div className={`text-xs font-bold group-hover:text-blue-500 truncate w-full ${isLight ? 'text-stone-700' : 'text-stone-300'}`}>
                                                            {h.name}
                                                        </div>
                                                        <div className="text-[9px] text-stone-500 font-mono uppercase mt-0.5">
                                                            {h.sub}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className={`p-3 border-t text-center ${isLight ? 'border-stone-100 bg-stone-50' : 'border-stone-800 bg-stone-950'}`}>
                    <p className="text-[10px] text-stone-500 uppercase tracking-widest">
                        Standard Model v6.1 • Generated by Spectrometer OS
                    </p>
                </div>
            </div>
        </div>
    );
};