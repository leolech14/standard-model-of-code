export type BoundaryType = 'Internal' | 'In' | 'Out' | 'In&Out';
export type ActivationType = 'Direct' | 'Event' | 'Time';
export type LifetimeType = 'Transient' | 'Session' | 'Global';
export type StateType = 'Stateless' | 'Stateful';
export type LayerType = 'Interface' | 'Application' | 'Domain' | 'Infra' | 'Core';
export type CategoryType = 'Data' | 'Logic' | 'Org' | 'Exec';

export type Theme = 'light' | 'dark';

export interface ColorPalette {
  data: number;
  logic: number;
  org: number;
  exec: number;
  chargeIn: number;
  chargeOut: number;
  chargeMix: number;
}

export interface Hadron {
  id: number;
  cat: CategoryType;
  sub: string;
  shape: string;
  name: string;
  desc: string;
  color: number;
  boundary: BoundaryType;
  lifetime: LifetimeType;
  state: StateType;
  layer: LayerType;
  targetY: number;
  activation: ActivationType;
}

export type ForceType = 'Strong' | 'Electromagnetic' | 'Weak' | 'Gravity' | 'Entanglement';

export interface Link {
  source: number;
  target: number;
  type: ForceType;
}

export interface PhysicsSettings {
  brownianStrength: number;
  drag: number;
  restitution: number;
  gravity: number;
  layerPull: number;
  kickStrength: number;
  blastRadius: number;
  higgsField: boolean;
  showForces: boolean;
  // New Forces
  darkEnergy: number;      // Repulsion/Expansion
  latticeStrength: number; // Grid Snapping
  quantumFlux: number;     // Wave Motion
}