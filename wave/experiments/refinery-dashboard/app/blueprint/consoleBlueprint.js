const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

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

export function resolveTheme(themeId) {
  return THEME_BLUEPRINT[themeId] || THEME_BLUEPRINT.paper;
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
