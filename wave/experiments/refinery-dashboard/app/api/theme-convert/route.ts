import { NextResponse } from "next/server";
import {
  convertGenomeSchemaToUiSources,
  listGenomeConverterTargets,
} from "../../blueprint/genomeConverters";

type ConverterRequest = {
  themeId?: string;
  seed?: string;
  genome?: Record<string, unknown>;
  targets?: string[];
  collection?: string;
  mode?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const parseString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim().length > 0 ? value.trim() : undefined;

const parseTargets = (value: unknown): string[] | undefined => {
  if (!value) return undefined;
  if (typeof value === "string") {
    return value
      .split(",")
      .map((target) => target.trim())
      .filter((target) => target.length > 0);
  }
  if (Array.isArray(value)) {
    return value
      .filter((item): item is string => typeof item === "string")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  }
  return undefined;
};

const parseRequestBody = (raw: unknown): ConverterRequest => {
  if (!isRecord(raw)) return {};
  const genome = isRecord(raw.genome) ? raw.genome : undefined;
  return {
    themeId: parseString(raw.themeId),
    seed: parseString(raw.seed),
    genome,
    targets: parseTargets(raw.targets),
    collection: parseString(raw.collection),
    mode: parseString(raw.mode),
  };
};

export async function GET() {
  return NextResponse.json({
    success: true,
    supportedTargets: listGenomeConverterTargets(),
    requestShape: {
      themeId: "machine | paper | midnight | vellum",
      seed: "optional string",
      genome: "optional genome object",
      targets: "optional array or comma-separated targets",
      collection: "optional figma/design collection name",
      mode: "optional target mode name",
    },
  });
}

export async function POST(request: Request) {
  try {
    const rawBody: unknown = await request.json();
    const payload = parseRequestBody(rawBody);
    const conversion = convertGenomeSchemaToUiSources(payload);

    return NextResponse.json({
      success: true,
      ...conversion,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Unknown converter error";
    return NextResponse.json(
      {
        success: false,
        error: message,
        supportedTargets: listGenomeConverterTargets(),
      },
      { status: 400 }
    );
  }
}
