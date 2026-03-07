const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const wrapHue = (value) => ((value % 360) + 360) % 360;
const oklch = (l, c, h) => `oklch(${(clamp(l, 0, 1) * 100).toFixed(1)}% ${clamp(c, 0, 0.37).toFixed(3)} ${wrapHue(h).toFixed(1)})`;

const hashSeed = (seedInput) => {
  const text = String(seedInput ?? "rainmaker-theme-machine");
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
};

const mulberry32 = (seed) => {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
};

const jitter = (rng, span) => (rng() * 2 - 1) * span;

export const TOKEN_REFS = {
  bg0: "var(--bg-0)",
  bg1: "var(--bg-1)",
  bg2: "var(--bg-2)",
  line: "var(--line)",
  ink0: "var(--ink-0)",
  ink1: "var(--ink-1)",
  ink2: "var(--ink-2)",
  ink3: "var(--ink-3)",
  blue: "var(--blue)",
  blueSoft: "var(--blue-soft)",
  teal: "var(--teal)",
  tealSoft: "var(--teal-soft)",
  green: "var(--green)",
  greenSoft: "var(--green-soft)",
  amber: "var(--amber)",
  amberSoft: "var(--amber-soft)",
  red: "var(--red)",
  redSoft: "var(--red-soft)",
  violet: "var(--violet)",
  violetSoft: "var(--violet-soft)",
  overlay: "var(--overlay-color)",
  shadow: "var(--shadow-color)",
};

export const THEME_BLUEPRINT = {
  paper: {
    id: "paper",
    label: "Paper",
    iconKey: "paper",
    bg0: "oklch(98.6% 0.002 250)",
    bg1: "oklch(97.2% 0.003 250)",
    bg2: "oklch(94.8% 0.004 250)",
    line: "oklch(89% 0.004 250)",
    ink0: "oklch(18% 0.01 250)",
    ink1: "oklch(28% 0.008 250)",
    ink2: "oklch(52% 0.006 250)",
    ink3: "oklch(72% 0.004 250)",
    blue: "oklch(62% 0.16 252)",
    blueSoft: "oklch(96.5% 0.018 252)",
    teal: "oklch(70% 0.13 190)",
    tealSoft: "oklch(96.7% 0.018 190)",
    green: "oklch(74% 0.14 145)",
    greenSoft: "oklch(97% 0.02 145)",
    amber: "oklch(80% 0.14 85)",
    amberSoft: "oklch(97% 0.022 85)",
    red: "oklch(64% 0.18 25)",
    redSoft: "oklch(96.5% 0.02 25)",
    violet: "oklch(60% 0.16 305)",
    violetSoft: "oklch(96% 0.018 305)",
    overlay: "rgba(255,255,255,0.55)",
    shadow: "rgba(0,0,0,0.08)",
  },
  midnight: {
    id: "midnight",
    label: "Midnight",
    iconKey: "midnight",
    bg0: "oklch(21% 0.012 255)",
    bg1: "oklch(25% 0.012 255)",
    bg2: "oklch(17% 0.01 255)",
    line: "oklch(34% 0.01 255)",
    ink0: "oklch(95% 0.004 255)",
    ink1: "oklch(88% 0.005 255)",
    ink2: "oklch(71% 0.006 255)",
    ink3: "oklch(56% 0.006 255)",
    blue: "oklch(74% 0.13 252)",
    blueSoft: "oklch(28% 0.03 252)",
    teal: "oklch(80% 0.11 190)",
    tealSoft: "oklch(30% 0.03 190)",
    green: "oklch(82% 0.12 145)",
    greenSoft: "oklch(30% 0.03 145)",
    amber: "oklch(86% 0.12 85)",
    amberSoft: "oklch(31% 0.03 85)",
    red: "oklch(76% 0.14 25)",
    redSoft: "oklch(29% 0.03 25)",
    violet: "oklch(78% 0.12 305)",
    violetSoft: "oklch(29% 0.03 305)",
    overlay: "rgba(8,10,14,0.55)",
    shadow: "rgba(0,0,0,0.28)",
  },
  vellum: {
    id: "vellum",
    label: "Vellum",
    iconKey: "vellum",
    bg0: "oklch(97.5% 0.01 80)",
    bg1: "oklch(95.8% 0.012 80)",
    bg2: "oklch(92.8% 0.014 80)",
    line: "oklch(86% 0.01 80)",
    ink0: "oklch(22% 0.012 55)",
    ink1: "oklch(34% 0.01 55)",
    ink2: "oklch(52% 0.008 55)",
    ink3: "oklch(70% 0.006 55)",
    blue: "oklch(60% 0.14 252)",
    blueSoft: "oklch(93.8% 0.02 252)",
    teal: "oklch(66% 0.11 190)",
    tealSoft: "oklch(94.2% 0.02 190)",
    green: "oklch(71% 0.11 145)",
    greenSoft: "oklch(94.8% 0.02 145)",
    amber: "oklch(78% 0.11 85)",
    amberSoft: "oklch(95.4% 0.02 85)",
    red: "oklch(62% 0.15 25)",
    redSoft: "oklch(94.5% 0.02 25)",
    violet: "oklch(58% 0.13 305)",
    violetSoft: "oklch(94.0% 0.02 305)",
    overlay: "rgba(247,240,228,0.58)",
    shadow: "rgba(72,52,26,0.10)",
  },
};

export const MACHINE_THEME_ID = "machine";

export function createThemeMachineGenome(seedInput = "rainmaker-seed") {
  const rng = mulberry32(hashSeed(seedInput));

  return {
    seed: String(seedInput),
    pivotHue: rng() * 360,
    hueSpread: 26 + rng() * 146,
    contrast: 0.12 + rng() * 0.86,
    energy: rng(),
    softness: rng(),
    warmth: rng() * 2 - 1,
    polarity: rng() * 2 - 1,
    noise: rng(),
  };
}

export function mutateThemeMachineGenome(genome, intensity = 0.38, seedInput = "mutation") {
  const rng = mulberry32(hashSeed(`${seedInput}:${genome.seed}:${genome.noise}`));
  const t = clamp(intensity, 0.05, 1);

  return {
    seed: `${genome.seed}:${Math.round(rng() * 1e8)}`,
    pivotHue: wrapHue(genome.pivotHue + jitter(rng, 220 * t)),
    hueSpread: clamp(genome.hueSpread + jitter(rng, 92 * t), 22, 174),
    contrast: clamp(genome.contrast + jitter(rng, 0.55 * t), 0.06, 0.99),
    energy: clamp(genome.energy + jitter(rng, 0.72 * t), 0, 1),
    softness: clamp(genome.softness + jitter(rng, 0.72 * t), 0, 1),
    warmth: clamp(genome.warmth + jitter(rng, 1.15 * t), -1, 1),
    polarity: clamp(genome.polarity + jitter(rng, 1.2 * t), -1, 1),
    noise: clamp(genome.noise + jitter(rng, 1.4 * t), 0, 1),
  };
}

export function resolveThemeMachine(genome) {
  const g = genome || createThemeMachineGenome("fallback");
  const lightMode = g.polarity >= 0;
  const neutralHue = wrapHue(g.pivotHue + g.warmth * 18);
  const contrastBand = 0.06 + g.contrast * 0.24;

  const bg0L = lightMode
    ? clamp(0.985 - contrastBand * 0.13 - g.softness * 0.065, 0.82, 0.99)
    : clamp(0.16 + g.softness * 0.095 + contrastBand * 0.08, 0.08, 0.34);
  const bg1L = lightMode
    ? clamp(bg0L - contrastBand * 0.19, 0.76, 0.98)
    : clamp(bg0L + contrastBand * 0.24, 0.11, 0.42);
  const bg2L = lightMode
    ? clamp(bg1L - contrastBand * 0.35, 0.62, 0.95)
    : clamp(bg0L - contrastBand * 0.22, 0.03, 0.26);

  const ink0L = lightMode
    ? clamp(0.14 + contrastBand * 0.35, 0.1, 0.34)
    : clamp(0.96 - contrastBand * 0.13, 0.76, 0.98);
  const ink1L = lightMode
    ? clamp(ink0L + 0.11, 0.19, 0.48)
    : clamp(ink0L - 0.09, 0.66, 0.92);
  const ink2L = lightMode
    ? clamp(ink1L + 0.22, 0.43, 0.72)
    : clamp(ink1L - 0.18, 0.42, 0.82);
  const ink3L = lightMode
    ? clamp(ink2L + 0.18, 0.6, 0.86)
    : clamp(ink2L - 0.17, 0.26, 0.7);

  const neutralC = lightMode
    ? 0.004 + g.softness * 0.014
    : 0.006 + g.softness * 0.011;
  const lineL = lightMode
    ? clamp(bg2L - contrastBand * 0.09, 0.54, 0.9)
    : clamp(bg1L + contrastBand * 0.08, 0.24, 0.52);

  const spreadScale = (g.hueSpread - 22) / 152;
  const hueStep = 34 + spreadScale * 137;
  const baseHue = wrapHue(g.pivotHue + g.warmth * 24);
  const hueOffsets = [0, 1, 2, 3, 4, 5].map((index) =>
    wrapHue(baseHue + index * hueStep + (index % 2 === 0 ? -1 : 1) * g.noise * 22)
  );

  const accentBaseC = clamp(0.07 + g.energy * 0.18 + (1 - g.softness) * 0.06, 0.05, 0.35);
  const accentBaseL = lightMode
    ? clamp(0.5 + g.energy * 0.23 + g.softness * 0.05, 0.47, 0.86)
    : clamp(0.68 + g.energy * 0.2 - g.softness * 0.05, 0.58, 0.94);
  const accentChromaScale = [0.98, 1.02, 0.95, 1.08, 1.1, 0.96];
  const accentLightBias = lightMode
    ? [0.02, 0.09, 0.16, 0.18, 0.11, 0.03]
    : [0.0, 0.06, 0.12, 0.15, 0.08, -0.02];

  const softBaseL = lightMode
    ? clamp(bg0L - 0.004 + g.softness * 0.022, 0.73, 0.99)
    : clamp(bg1L + 0.03 + g.softness * 0.04, 0.22, 0.52);
  const softBaseC = clamp(accentBaseC * 0.17, 0.012, 0.06);

  const accentNames = ["blue", "teal", "green", "amber", "red", "violet"];
  const accents = {};
  accentNames.forEach((name, index) => {
    accents[name] = oklch(accentBaseL + accentLightBias[index], accentBaseC * accentChromaScale[index], hueOffsets[index]);
    accents[`${name}Soft`] = oklch(
      softBaseL + (index % 2 === 0 ? 0.005 : -0.005),
      softBaseC * (index % 2 === 0 ? 1.06 : 0.94),
      hueOffsets[index]
    );
  });

  const overlayAlpha = lightMode
    ? clamp(0.42 + g.softness * 0.26, 0.35, 0.74)
    : clamp(0.46 + contrastBand * 0.72, 0.46, 0.78);
  const shadowAlpha = lightMode
    ? clamp(0.06 + contrastBand * 0.22, 0.05, 0.22)
    : clamp(0.2 + contrastBand * 0.35, 0.2, 0.48);

  return {
    id: MACHINE_THEME_ID,
    label: "Machine",
    iconKey: MACHINE_THEME_ID,
    bg0: oklch(bg0L, neutralC, neutralHue),
    bg1: oklch(bg1L, neutralC * 1.06, neutralHue + g.warmth * 6),
    bg2: oklch(bg2L, neutralC * 1.12, neutralHue - g.warmth * 7),
    line: oklch(lineL, neutralC * 1.35, neutralHue),
    ink0: oklch(ink0L, neutralC * 2.2, neutralHue - 3),
    ink1: oklch(ink1L, neutralC * 1.8, neutralHue - 2),
    ink2: oklch(ink2L, neutralC * 1.4, neutralHue + 2),
    ink3: oklch(ink3L, neutralC * 1.2, neutralHue + 3),
    ...accents,
    overlay: lightMode
      ? `rgba(255,255,255,${overlayAlpha.toFixed(3)})`
      : `rgba(5,8,12,${overlayAlpha.toFixed(3)})`,
    shadow: `rgba(0,0,0,${shadowAlpha.toFixed(3)})`,
  };
}

export const DOMAIN_BLUEPRINT = [
  { id: "overview", label: "Overview", iconKey: "overview", accentToken: "blue", softToken: "blueSoft", nodes: ["Today", "Priority", "Live", "Connections"] },
  { id: "work", label: "Work", iconKey: "work", accentToken: "teal", softToken: "tealSoft", nodes: ["Projects", "Files", "Calendar", "Map"] },
  { id: "intelligence", label: "Intelligence", iconKey: "intelligence", accentToken: "violet", softToken: "violetSoft", nodes: ["Rainmaker", "Refinery", "Automations", "Memory"] },
  { id: "runtime", label: "Runtime", iconKey: "runtime", accentToken: "green", softToken: "greenSoft", nodes: ["Runs", "Queues", "Logs", "Approvals"] },
  { id: "finance", label: "Finance", iconKey: "finance", accentToken: "amber", softToken: "amberSoft", nodes: ["Spend", "Burn", "Forecast", "Anomalies"] },
  { id: "system", label: "System", iconKey: "system", accentToken: "ink1", softToken: "bg2", nodes: ["Integrations", "Environments", "Observability", "Access"] },
];

export const RUNTIME_STRIP_BLUEPRINT = [
  { label: "Refinery #2471", state: "Running", toneToken: "greenSoft", inkToken: "green" },
  { label: "Drive index", state: "Queued", toneToken: "blueSoft", inkToken: "blue" },
  { label: "Burn rate", state: "$7.12 / h", toneToken: "amberSoft", inkToken: "amber" },
  { label: "Approvals", state: "3 pending", toneToken: "redSoft", inkToken: "red" },
  { label: "Gateway", state: "Live", toneToken: "tealSoft", inkToken: "teal" },
];

export function resolveTheme(themeId, machineGenome) {
  if (themeId === MACHINE_THEME_ID) {
    return resolveThemeMachine(machineGenome);
  }
  return THEME_BLUEPRINT[themeId] || THEME_BLUEPRINT.paper;
}

export function describeThemeMachine(genome) {
  return {
    hue: Math.round(wrapHue(genome.pivotHue)),
    spread: Math.round(genome.hueSpread),
    contrast: Math.round(genome.contrast * 100),
    energy: Math.round(genome.energy * 100),
    polarity: genome.polarity >= 0 ? "light-biased" : "dark-biased",
  };
}

export function createThemeCssVars(theme) {
  return {
    "--bg-0": theme.bg0,
    "--bg-1": theme.bg1,
    "--bg-2": theme.bg2,
    "--line": theme.line,
    "--ink-0": theme.ink0,
    "--ink-1": theme.ink1,
    "--ink-2": theme.ink2,
    "--ink-3": theme.ink3,
    "--blue": theme.blue,
    "--blue-soft": theme.blueSoft,
    "--teal": theme.teal,
    "--teal-soft": theme.tealSoft,
    "--green": theme.green,
    "--green-soft": theme.greenSoft,
    "--amber": theme.amber,
    "--amber-soft": theme.amberSoft,
    "--red": theme.red,
    "--red-soft": theme.redSoft,
    "--violet": theme.violet,
    "--violet-soft": theme.violetSoft,
    "--overlay-color": theme.overlay,
    "--shadow-color": theme.shadow,
  };
}

export function resolveDomains(iconRegistry, tokens = TOKEN_REFS) {
  return DOMAIN_BLUEPRINT.map((domain) => ({
    ...domain,
    icon: iconRegistry[domain.iconKey] || null,
    tint: tokens[domain.accentToken],
    soft: tokens[domain.softToken],
  }));
}

export function resolveRuntimeItems(tokens = TOKEN_REFS) {
  return RUNTIME_STRIP_BLUEPRINT.map((item) => ({
    ...item,
    tone: tokens[item.toneToken],
    ink: tokens[item.inkToken],
  }));
}

export function validateDomainScreens(domains, screens) {
  const errors = [];

  domains.forEach((domain) => {
    if (!screens[domain.id]) {
      errors.push(`Missing screen group for domain: ${domain.id}`);
      return;
    }

    domain.nodes.forEach((node) => {
      const screen = screens[domain.id][node];
      if (!screen) {
        errors.push(`Missing screen config for ${domain.id}.${node}`);
        return;
      }

      if (!Array.isArray(screen.status)) errors.push(`status must be an array for ${domain.id}.${node}`);
      if (!Array.isArray(screen.metrics)) errors.push(`metrics must be an array for ${domain.id}.${node}`);
      if (!Array.isArray(screen.sections)) errors.push(`sections must be an array for ${domain.id}.${node}`);
      if (!screen.inspector || !Array.isArray(screen.inspector.facts)) {
        errors.push(`inspector.facts must be an array for ${domain.id}.${node}`);
      }
    });
  });

  return errors;
}

export const SHELL_GRID_ROW_CLASS = "lg:grid-rows-[var(--header-h)_minmax(0,1fr)_var(--footer-h)]";

export function resolveShellColumnClass(sidebarOpen, inspectorOpen) {
  if (sidebarOpen && inspectorOpen) {
    return "lg:[grid-template-columns:var(--rail-w)_var(--sidebar-w)_minmax(0,1fr)_var(--inspector-w)]";
  }
  if (sidebarOpen && !inspectorOpen) {
    return "lg:[grid-template-columns:var(--rail-w)_var(--sidebar-w)_minmax(0,1fr)]";
  }
  if (!sidebarOpen && inspectorOpen) {
    return "lg:[grid-template-columns:minmax(0,1fr)_var(--inspector-w)]";
  }
  return "lg:[grid-template-columns:minmax(0,1fr)]";
}

export function deriveLayoutVars(viewport) {
  const width = clamp(viewport?.width || 1440, 320, 4096);
  const height = clamp(viewport?.height || 900, 320, 2160);
  const unit = Math.min(width, height);
  const px = (value) => `${Math.round(value)}px`;

  const shellMinH = height * 0.88;
  const shellMaxW = Math.min(width * 0.94, 1780);
  const shellRadius = clamp(unit * 0.031, 20, 36);
  const headerH = clamp(height * 0.062, 52, 70);
  const footerH = clamp(height * 0.043, 36, 52);
  const railW = clamp(width * 0.05, 64, 84);
  const sidebarW = clamp(width * 0.17, 220, 280);
  const inspectorW = clamp(width * 0.23, 280, 380);
  const commandW = clamp(width * 0.62, 720, 980);
  const commandTop = clamp(height * 0.08, 42, 96);
  const commandPad = clamp(unit * 0.034, 16, 48);
  const mapMinH = clamp(height * 0.31, 220, 360);
  const mapGrid = clamp(unit * 0.055, 36, 72);
  const surfaceRadius = clamp(unit * 0.028, 20, 34);
  const panelRadius = clamp(unit * 0.022, 16, 28);
  const brandW = clamp(width * 0.15, 190, 280);
  const toolbarMin = clamp(width * 0.21, 280, 420);

  return {
    "--shell-min-h": px(shellMinH),
    "--shell-max-w": px(shellMaxW),
    "--shell-radius": px(shellRadius),
    "--header-h": px(headerH),
    "--footer-h": px(footerH),
    "--rail-w": px(railW),
    "--sidebar-w": px(sidebarW),
    "--inspector-w": px(inspectorW),
    "--command-max-w": px(commandW),
    "--command-top": px(commandTop),
    "--command-overlay-pad": px(commandPad),
    "--map-min-h": px(mapMinH),
    "--map-grid-size": px(mapGrid),
    "--surface-radius": px(surfaceRadius),
    "--panel-radius": px(panelRadius),
    "--brand-w": px(brandW),
    "--toolbar-min": px(toolbarMin),
  };
}
