import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  convertGenomeSchemaToUiSources,
  listGenomeConverterTargets,
} from "../app/blueprint/genomeConverters.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");
const TARGETS = listGenomeConverterTargets();
const OUT_ROOT = path.join(ROOT_DIR, "assets", "theme-source-snapshots");

const EXPORT_SETS = [
  { id: "paper", themeId: "paper", mode: "Paper" },
  { id: "midnight", themeId: "midnight", mode: "Midnight" },
  { id: "vellum", themeId: "vellum", mode: "Vellum" },
  { id: "machine-alpha", themeId: "machine", seed: "rainmaker-machine-alpha", mode: "Machine Alpha" },
  { id: "machine-beta", themeId: "machine", seed: "rainmaker-machine-beta", mode: "Machine Beta" },
  { id: "machine-gamma", themeId: "machine", seed: "rainmaker-machine-gamma", mode: "Machine Gamma" },
];

const writeJson = async (filePath, value) => {
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
};

const writeSet = async (setConfig) => {
  const conversion = convertGenomeSchemaToUiSources({
    themeId: setConfig.themeId,
    seed: setConfig.seed,
    targets: TARGETS,
    collection: "Rainmaker Console Theme Machine",
    mode: setConfig.mode,
  });

  const setDir = path.join(OUT_ROOT, setConfig.id);
  await fs.mkdir(setDir, { recursive: true });

  await writeJson(path.join(setDir, "bundle.json"), conversion);
  await writeJson(path.join(setDir, "metadata.json"), conversion.metadata);
  await writeJson(path.join(setDir, "theme.json"), conversion.theme);

  if (conversion.genome) {
    await writeJson(path.join(setDir, "genome.json"), conversion.genome);
  }

  await writeJson(path.join(setDir, "figma-variables.json"), conversion.outputs["figma-variables"]);
  await writeJson(path.join(setDir, "design-tokens.json"), conversion.outputs["design-tokens"]);
  await writeJson(path.join(setDir, "tailwind.json"), conversion.outputs.tailwind);
  await writeJson(path.join(setDir, "mui.json"), conversion.outputs.mui);
  await writeJson(path.join(setDir, "chakra.json"), conversion.outputs.chakra);
  await writeJson(path.join(setDir, "css-vars.json"), conversion.outputs["css-vars"].variables);
  await fs.writeFile(path.join(setDir, "css-vars.css"), `${conversion.outputs["css-vars"].cssText}\n`, "utf8");
};

const writeGlobalManifest = async () => {
  const manifest = {
    generatedAt: new Date().toISOString(),
    targets: TARGETS,
    sets: EXPORT_SETS.map((setConfig) => ({
      id: setConfig.id,
      themeId: setConfig.themeId,
      seed: setConfig.seed || null,
      mode: setConfig.mode,
      outputDir: path.relative(ROOT_DIR, path.join(OUT_ROOT, setConfig.id)),
    })),
  };
  await writeJson(path.join(OUT_ROOT, "manifest.json"), manifest);
};

const main = async () => {
  await fs.mkdir(OUT_ROOT, { recursive: true });
  for (const setConfig of EXPORT_SETS) {
    await writeSet(setConfig);
  }
  await writeGlobalManifest();
  console.log(`exported ${EXPORT_SETS.length} theme sets to ${path.relative(ROOT_DIR, OUT_ROOT)}`);
};

main().catch((error) => {
  console.error("failed to export theme assets:", error);
  process.exitCode = 1;
});
