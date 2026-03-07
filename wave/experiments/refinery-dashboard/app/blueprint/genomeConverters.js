import {
  MACHINE_THEME_ID,
  THEME_BLUEPRINT,
  TOKEN_REFS,
  createThemeMachineGenome,
  resolveTheme,
} from "./consoleBlueprint";

const CSS_VAR_REF_PATTERN = /^var\((--[^)]+)\)$/;

const TOKEN_NAME_MAP = {
  bg0: "background/base",
  bg1: "background/surface",
  bg2: "background/elevated",
  line: "stroke/default",
  ink0: "text/primary",
  ink1: "text/strong",
  ink2: "text/muted",
  ink3: "text/subtle",
  blue: "accent/blue/main",
  blueSoft: "accent/blue/soft",
  teal: "accent/teal/main",
  tealSoft: "accent/teal/soft",
  green: "accent/green/main",
  greenSoft: "accent/green/soft",
  amber: "accent/amber/main",
  amberSoft: "accent/amber/soft",
  red: "accent/red/main",
  redSoft: "accent/red/soft",
  violet: "accent/violet/main",
  violetSoft: "accent/violet/soft",
  overlay: "effect/overlay",
  shadow: "effect/shadow",
};

const TARGETS = ["css-vars", "figma-variables", "design-tokens", "tailwind", "mui", "chakra"];

const toCssVarName = (tokenRef) => {
  const match = CSS_VAR_REF_PATTERN.exec(tokenRef);
  return match ? match[1] : tokenRef;
};

const tokenEntriesFromTheme = (theme) =>
  Object.entries(TOKEN_REFS).map(([key, tokenRef]) => {
    const cssVar = toCssVarName(tokenRef);
    return {
      key,
      cssVar,
      path: TOKEN_NAME_MAP[key] || key,
      value: theme[key],
    };
  });

const asCssVarMap = (entries) =>
  entries.reduce((acc, entry) => {
    acc[entry.cssVar] = entry.value;
    return acc;
  }, {});

const asSemanticMap = (entries) =>
  entries.reduce((acc, entry) => {
    acc[entry.path] = entry.value;
    return acc;
  }, {});

const toDesignTokenTree = (entries) => {
  const root = {};

  entries.forEach((entry) => {
    const segments = entry.path.split("/");
    let cursor = root;
    segments.forEach((segment, index) => {
      const leaf = index === segments.length - 1;
      if (leaf) {
        cursor[segment] = {
          $type: "color",
          $value: entry.value,
        };
        return;
      }
      cursor[segment] = cursor[segment] || {};
      cursor = cursor[segment];
    });
  });

  return root;
};

const buildCssVarsPayload = (entries) => {
  const variables = asCssVarMap(entries);
  const cssLines = Object.entries(variables).map(([name, value]) => `  ${name}: ${value};`);
  return {
    variables,
    cssText: [":root {", ...cssLines, "}"].join("\n"),
  };
};

const buildFigmaVariablesPayload = (entries, metadata) => ({
  collection: metadata.collection || "Rainmaker Theme Machine",
  mode: metadata.mode || metadata.themeLabel,
  variables: entries.map((entry) => ({
    name: entry.path,
    resolvedType: "COLOR",
    value: entry.value,
    codeSyntax: {
      WEB: `var(${entry.cssVar})`,
    },
  })),
});

const buildDesignTokensPayload = (entries, metadata) => ({
  $schema: "https://tr.designtokens.org/format/schema.json",
  $description: `Theme tokens generated from genome seed ${metadata.seed}`,
  color: toDesignTokenTree(entries),
});

const buildTailwindPayload = (entries, theme) => {
  const colors = entries.reduce((acc, entry) => {
    acc[`rm-${entry.key}`] = entry.value;
    return acc;
  }, {});

  return {
    theme: {
      extend: {
        colors,
        boxShadow: {
          "rm-shell": `0 24px 80px ${theme.shadow}`,
        },
      },
    },
  };
};

const buildMUIThemePayload = (theme, metadata) => {
  const mode = metadata.themeId === MACHINE_THEME_ID
    ? metadata.polarity
    : metadata.themeId === "midnight"
      ? "dark"
      : "light";

  return {
    palette: {
      mode,
      background: {
        default: theme.bg2,
        paper: theme.bg0,
      },
      text: {
        primary: theme.ink0,
        secondary: theme.ink2,
        disabled: theme.ink3,
      },
      divider: theme.line,
      primary: { main: theme.blue, light: theme.blueSoft },
      secondary: { main: theme.violet, light: theme.violetSoft },
      success: { main: theme.green, light: theme.greenSoft },
      warning: { main: theme.amber, light: theme.amberSoft },
      error: { main: theme.red, light: theme.redSoft },
      info: { main: theme.teal, light: theme.tealSoft },
    },
    custom: {
      overlay: theme.overlay,
      shadow: theme.shadow,
    },
  };
};

const buildChakraPayload = (entries, theme) => ({
  semanticTokens: {
    colors: asSemanticMap(entries),
  },
  shadows: {
    shell: `0 24px 80px ${theme.shadow}`,
  },
});

const resolveTargetPayload = (target, entries, theme, metadata) => {
  if (target === "css-vars") return buildCssVarsPayload(entries);
  if (target === "figma-variables") return buildFigmaVariablesPayload(entries, metadata);
  if (target === "design-tokens") return buildDesignTokensPayload(entries, metadata);
  if (target === "tailwind") return buildTailwindPayload(entries, theme);
  if (target === "mui") return buildMUIThemePayload(theme, metadata);
  if (target === "chakra") return buildChakraPayload(entries, theme);
  throw new Error(`Unsupported converter target: ${target}`);
};

const resolveTargets = (targetsInput) => {
  if (!targetsInput || targetsInput.length === 0) return TARGETS;
  const normalized = Array.from(new Set(targetsInput.map((target) => String(target).toLowerCase())));
  normalized.forEach((target) => {
    if (!TARGETS.includes(target)) {
      throw new Error(`Invalid target "${target}". Supported: ${TARGETS.join(", ")}`);
    }
  });
  return normalized;
};

const normalizeGenome = (genomeInput, seedInput) => {
  if (genomeInput && typeof genomeInput === "object") {
    return genomeInput;
  }
  return createThemeMachineGenome(seedInput || "rainmaker-machine-export");
};

const resolveThemeFromInput = ({ themeId, seed, genome }) => {
  const id = themeId || MACHINE_THEME_ID;
  if (id === MACHINE_THEME_ID) {
    const normalizedGenome = normalizeGenome(genome, seed);
    const theme = resolveTheme(id, normalizedGenome);
    return { theme, genome: normalizedGenome, themeId: id };
  }
  const fallbackTheme = THEME_BLUEPRINT[id] ? resolveTheme(id) : resolveTheme("paper");
  return { theme: fallbackTheme, genome: null, themeId: THEME_BLUEPRINT[id] ? id : "paper" };
};

const derivePolarity = (theme) => {
  const lightness = (value) => {
    const match = /oklch\(([\d.]+)%/.exec(String(value));
    return match ? Number(match[1]) : 50;
  };
  return lightness(theme.bg0) > 50 ? "light" : "dark";
};

export function listGenomeConverterTargets() {
  return [...TARGETS];
}

export function convertGenomeSchemaToUiSources(options = {}) {
  const targets = resolveTargets(options.targets);
  const resolved = resolveThemeFromInput({
    themeId: options.themeId,
    seed: options.seed,
    genome: options.genome,
  });
  const entries = tokenEntriesFromTheme(resolved.theme);
  const metadata = {
    generatedAt: new Date().toISOString(),
    seed: options.seed || resolved.genome?.seed || "n/a",
    themeId: resolved.themeId,
    themeLabel: resolved.theme.label || resolved.themeId,
    polarity: derivePolarity(resolved.theme),
    collection: options.collection || "Rainmaker Theme Machine",
    mode: options.mode || resolved.theme.label || resolved.themeId,
  };

  const outputs = targets.reduce((acc, target) => {
    acc[target] = resolveTargetPayload(target, entries, resolved.theme, metadata);
    return acc;
  }, {});

  return {
    metadata,
    genome: resolved.genome,
    theme: resolved.theme,
    outputs,
  };
}
