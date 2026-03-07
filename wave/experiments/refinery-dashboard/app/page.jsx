"use client";

import React, { startTransition, useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  SHELL_GRID_ROW_CLASS,
  THEME_BLUEPRINT,
  TOKEN_REFS,
  createThemeCssVars,
  deriveLayoutVars,
  resolveDomains,
  resolveRuntimeItems,
  resolveShellColumnClass,
  resolveTheme,
  validateDomainScreens,
} from "./blueprint/consoleBlueprint";

function IconBase({ className = "h-4 w-4", style, children, viewBox = "0 0 16 16" }) {
  return (
    <svg
      viewBox={viewBox}
      className={className}
      style={style}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

function MarkGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="8" cy="8" r="1.6" />
      <path d="M8 2v2.1M8 11.9V14M2 8h2.1M11.9 8H14M3.7 3.7l1.4 1.4M10.9 10.9l1.4 1.4M12.3 3.7l-1.4 1.4M5.1 10.9l-1.4 1.4" />
    </IconBase>
  );
}

function SearchGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="7" cy="7" r="3.5" />
      <path d="M10 10l3 3" />
    </IconBase>
  );
}

function ArrowGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M6 4l4 4-4 4" />
    </IconBase>
  );
}

function BellGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M5.3 11.2h5.4" />
      <path d="M6 11.2V7.1a2 2 0 114 0v4.1" />
      <path d="M5 11.2c0-.7.5-1.2 1.2-1.2h3.6c.7 0 1.2.5 1.2 1.2" />
      <path d="M7.2 12.6a.8.8 0 001.6 0" />
    </IconBase>
  );
}

function OverviewGlyph(props) {
  return (
    <IconBase {...props}>
      <rect x="2.5" y="2.5" width="4" height="4" rx="1" />
      <rect x="9.5" y="2.5" width="4" height="4" rx="1" />
      <rect x="2.5" y="9.5" width="4" height="4" rx="1" />
      <rect x="9.5" y="9.5" width="4" height="4" rx="1" />
    </IconBase>
  );
}

function WorkGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M3 4.5h4.2l1.1 1.6H13" />
      <path d="M3 6.8h10v4.7H3z" />
    </IconBase>
  );
}

function IntelligenceGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="8" cy="8" r="1.2" />
      <path d="M8 2.6c2.8 0 5 2.4 5 5.4s-2.2 5.4-5 5.4S3 11 3 8s2.2-5.4 5-5.4z" />
      <path d="M4.6 4.8c1.2.9 2.2 1.3 3.4 1.3s2.2-.4 3.4-1.3" />
      <path d="M4.6 11.2c1.2-.9 2.2-1.3 3.4-1.3s2.2.4 3.4 1.3" />
    </IconBase>
  );
}

function RuntimeGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M2 8h2.5l1.5-3 2.2 6 1.7-3H14" />
    </IconBase>
  );
}

function FinanceGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M3 12.5h10" />
      <path d="M4.5 10V6.5" />
      <path d="M8 10V4" />
      <path d="M11.5 10V7.5" />
    </IconBase>
  );
}

function SystemGlyph(props) {
  return (
    <IconBase {...props}>
      <rect x="4" y="4" width="8" height="8" rx="1.8" />
      <path d="M8 1.8v2M8 12.2v2M1.8 8h2M12.2 8h2" />
    </IconBase>
  );
}

function PaperThemeGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="8" cy="8" r="3" />
      <path d="M8 1.8v1.8M8 12.4v1.8M1.8 8h1.8M12.4 8h1.8" />
    </IconBase>
  );
}

function MidnightThemeGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M10.8 2.5a4.9 4.9 0 100 11 5.5 5.5 0 01-3.3-5.5c0-2.2 1.2-4.2 3.3-5.5z" />
    </IconBase>
  );
}

function VellumThemeGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M4 2.8h6l2 2v8.4H4z" />
      <path d="M10 2.8v2h2" />
      <path d="M6 8h4M6 10.5h3" />
    </IconBase>
  );
}

function TreeGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="4" cy="4" r="1" />
      <circle cx="12" cy="4" r="1" />
      <circle cx="8" cy="12" r="1" />
      <path d="M4 5.2v2h4v3.6M12 5.2v2H8" />
    </IconBase>
  );
}

function StorageGlyph(props) {
  return (
    <IconBase {...props}>
      <ellipse cx="8" cy="4.2" rx="4.2" ry="1.8" />
      <path d="M3.8 4.2v5.2c0 1 1.9 1.8 4.2 1.8s4.2-.8 4.2-1.8V4.2" />
      <path d="M3.8 7c0 1 1.9 1.8 4.2 1.8s4.2-.8 4.2-1.8" />
    </IconBase>
  );
}

function AgentGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="8" cy="8" r="1.4" />
      <path d="M8 3.2c2.6 0 4.8 2.1 4.8 4.8S10.6 12.8 8 12.8 3.2 10.6 3.2 8 5.4 3.2 8 3.2z" />
      <path d="M8 1.8v1.4M8 12.8v1.4M1.8 8h1.4M12.8 8h1.4" />
    </IconBase>
  );
}

function GuardGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M8 2.2l4.4 1.9v3.4c0 2.3-1.5 4.4-4.4 6.3-2.9-1.9-4.4-4-4.4-6.3V4.1z" />
    </IconBase>
  );
}

function CloudGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M5.1 11.4H11a2.3 2.3 0 000-4.6h-.4A3.1 3.1 0 005 7.1 2.1 2.1 0 005.1 11.4z" />
    </IconBase>
  );
}

function CalendarGlyph(props) {
  return (
    <IconBase {...props}>
      <rect x="3" y="4" width="10" height="9" rx="1.5" />
      <path d="M5.5 2.5v2.2M10.5 2.5v2.2M3 6.8h10" />
    </IconBase>
  );
}

function MapGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="8" cy="8" r="2.2" />
      <path d="M8 2.2v2M8 11.8v2M2.2 8h2M11.8 8h2" />
    </IconBase>
  );
}

function FlowGlyph(props) {
  return (
    <IconBase {...props}>
      <circle cx="3.5" cy="8" r="1.2" />
      <circle cx="12.5" cy="4.5" r="1.2" />
      <circle cx="12.5" cy="11.5" r="1.2" />
      <path d="M4.8 8h3.4l2.9-2.5M8.2 8h2.9" />
    </IconBase>
  );
}

function StackGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M3.2 4.8h9.6M3.2 8h9.6M3.2 11.2h9.6" />
      <circle cx="5" cy="4.8" r=".5" fill="currentColor" stroke="none" />
      <circle cx="8.2" cy="8" r=".5" fill="currentColor" stroke="none" />
      <circle cx="11" cy="11.2" r=".5" fill="currentColor" stroke="none" />
    </IconBase>
  );
}

function BoltGlyph(props) {
  return (
    <IconBase {...props}>
      <path d="M8.8 2.5L5.2 8h2.3L7 13.5 10.8 8H8.5z" />
    </IconBase>
  );
}

const TOKENS = TOKEN_REFS;

const ICON_REGISTRY = {
  overview: OverviewGlyph,
  work: WorkGlyph,
  intelligence: IntelligenceGlyph,
  runtime: RuntimeGlyph,
  finance: FinanceGlyph,
  system: SystemGlyph,
};

const THEME_ICON_REGISTRY = {
  paper: PaperThemeGlyph,
  midnight: MidnightThemeGlyph,
  vellum: VellumThemeGlyph,
};

const THEME_CHOICES = Object.values(THEME_BLUEPRINT).map((theme) => ({
  ...theme,
  icon: THEME_ICON_REGISTRY[theme.iconKey],
}));

const SCREENS = {
  overview: {
    Today: {
      eyebrow: "Overview / Today",
      title: "Operational surface",
      description: "A single stable window for projects, agents, runtime, files, costs and coordination.",
      status: [
        { label: "Workspace", value: "Rainmaker / Cloud" },
        { label: "Mode", value: "Operator" },
        { label: "Sync", value: "Live" },
      ],
      metrics: [
        { label: "Active runs", value: "12", delta: "+3" },
        { label: "Agent sessions", value: "5", delta: "+1" },
        { label: "Today cost", value: "$46.80", delta: "stable" },
        { label: "Pending approvals", value: "3", delta: "needs review" },
      ],
      sections: [
        {
          label: "Priority",
          title: "What requires attention now",
          type: "list",
          items: [
            ["Refinery", "Context batch #247 is waiting for final validation."],
            ["Rainmaker", "Agent memory sync completed. Review 2 new route suggestions."],
            ["Cloud", "Compute burn increased 11% after the overnight trading run."],
          ],
        },
        {
          label: "Live",
          title: "Active runtime",
          type: "timeline",
          items: [
            ["16:29", "Trading strategy backtest completed on cloud-eu-2."],
            ["16:24", "Calendar sync imported 8 events into work surfaces."],
            ["16:18", "Rainmaker approved a low-risk file reorganization plan."],
            ["16:03", "Context refinery spawned a new comparison job for legal corpus."],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Rainmaker agent / overview",
        facts: [
          ["State", "Healthy"],
          ["Goal", "Coordinate work surfaces"],
          ["Recent cost", "$7.12 / h"],
          ["Relations", "Projects · Files · Runtime"],
        ],
      },
    },
    Priority: {
      eyebrow: "Overview / Priority",
      title: "Attention routing",
      description: "The shell exposes urgency without changing its geometry. Priority appears as state, not as a separate app.",
      status: [
        { label: "Urgent", value: "2" },
        { label: "Review", value: "5" },
        { label: "Blocked", value: "1" },
      ],
      metrics: [
        { label: "Workstreams", value: "7", delta: "tracked" },
        { label: "High cost nodes", value: "2", delta: "visible" },
        { label: "Decision latency", value: "11m", delta: "good" },
        { label: "Escalations", value: "1", delta: "manual" },
      ],
      sections: [
        {
          label: "Queues",
          title: "Approval stack",
          type: "table",
          columns: ["Item", "Owner", "Risk", "ETA"],
          rows: [
            ["Context merge / legal", "Rainmaker", "Medium", "Today"],
            ["Trading config delta", "Operator", "High", "Now"],
            ["Drive folder sync", "Automation", "Low", "Queued"],
          ],
        },
        {
          label: "Notes",
          title: "Operational reasoning",
          type: "paragraph",
          text: "Priority lives inside the same scaffold as everything else. The UI stays calm while the system remains explicit about urgency, cost and risk.",
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Approval / trading config delta",
        facts: [
          ["State", "Awaiting decision"],
          ["Cost impact", "+$9.40 forecast"],
          ["Scope", "Runtime / Strategy 03"],
          ["Source", "Overnight anomaly detector"],
        ],
      },
    },
    Live: {
      eyebrow: "Overview / Live",
      title: "Activity field",
      description: "A persistent control surface for everything that is moving right now.",
      status: [
        { label: "Signals", value: "14" },
        { label: "Errors", value: "0 critical" },
        { label: "Connected", value: "11 systems" },
      ],
      metrics: [
        { label: "Event rate", value: "28/min", delta: "steady" },
        { label: "Queue depth", value: "7", delta: "normal" },
        { label: "CPU cloud", value: "63%", delta: "+4" },
        { label: "Latency", value: "182ms", delta: "good" },
      ],
      sections: [
        {
          label: "Runtime",
          title: "Signal stream",
          type: "timeline",
          items: [
            ["agent", "Rainmaker produced a routing recommendation for refinery output."],
            ["queue", "3 file indexing tasks moved into active processing."],
            ["calendar", "Google Calendar webhook acknowledged and normalized."],
            ["finance", "Burn-rate line crossed soft threshold; alert downgraded after cooldown."],
          ],
        },
        {
          label: "Shape",
          title: "System density",
          type: "bars",
          items: [["Agents", 74], ["Automations", 58], ["Project IO", 83], ["Calendar", 34], ["Cloud", 66]],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Live field / runtime stream",
        facts: [["Window", "Last 30 minutes"], ["Most active", "Project IO"], ["Noise", "Low"], ["Retention", "Hot cache"]],
      },
    },
    Connections: {
      eyebrow: "Overview / Connections",
      title: "Connected surfaces",
      description: "Configuration belongs to System, but the visibility of connected surfaces belongs to the operational shell.",
      status: [
        { label: "Healthy", value: "8" },
        { label: "Degraded", value: "1" },
        { label: "Sync age", value: "< 2m" },
      ],
      metrics: [
        { label: "Google Calendar", value: "Live", delta: "2m ago" },
        { label: "Google Drive", value: "Live", delta: "1m ago" },
        { label: "Cloud storage", value: "Healthy", delta: "steady" },
        { label: "OpenClaw", value: "Gateway", delta: "primary" },
      ],
      sections: [
        {
          label: "Map",
          title: "Connected systems",
          type: "list",
          items: [
            ["Calendar", "Events and availability flow into Work surfaces."],
            ["Drive", "Artifacts, context packs and exports available in Files."],
            ["Cloud", "Agents, jobs and telemetry routed through runtime backbone."],
            ["Gateway", "Stable control plane backing the whole console shell."],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "OpenClaw gateway",
        facts: [["State", "Primary"], ["Role", "Control plane"], ["Clients", "Web · Agents · Automations"], ["Transport", "WebSocket"]],
      },
    },
  },
  work: {
    Projects: {
      eyebrow: "Work / Projects",
      title: "Project field",
      description: "Projects, artifacts and schedules sit inside one quiet operational frame.",
      status: [{ label: "Active", value: "9 projects" }, { label: "Focus", value: "3 high" }, { label: "Drive", value: "Synced" }],
      metrics: [
        { label: "OpenClaw", value: "Core build", delta: "active" },
        { label: "Refinery", value: "v0.3", delta: "moving" },
        { label: "Trading", value: "2 strategies", delta: "live" },
        { label: "Docs", value: "41 assets", delta: "+6" },
      ],
      sections: [
        {
          label: "Collection",
          title: "Projects",
          type: "table",
          columns: ["Name", "Mode", "Owner", "Health"],
          rows: [
            ["OpenClaw", "Core platform", "Leonardo", "Healthy"],
            ["Rainmaker UI", "Design system", "Leonardo", "Exploring"],
            ["Refinery", "Context processing", "Rainmaker", "Review"],
            ["Trading Ops", "Realtime", "Automation", "Live"],
          ],
        },
        {
          label: "Activity",
          title: "Recent project movement",
          type: "timeline",
          items: [
            ["Rainmaker UI", "Wireframe export added to design artifacts."],
            ["Refinery", "Comparison layer generated 14 candidate merges."],
            ["Trading Ops", "New strategy branch validated on historical slice."],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Project / Rainmaker UI",
        facts: [["State", "Exploring"], ["Surface", "Shell architecture"], ["Artifacts", "12"], ["Next", "Component spec"]],
      },
    },
    Files: {
      eyebrow: "Work / Files",
      title: "Explorer surface",
      description: "Files should feel like another lens over the same world, not like a separate application.",
      status: [{ label: "Root", value: "/rainmaker" }, { label: "Index", value: "Ready" }, { label: "Preview", value: "Inspector" }],
      metrics: [
        { label: "Files", value: "14,228", delta: "indexed" },
        { label: "Recent", value: "22", delta: "24h" },
        { label: "Queued OCR", value: "6", delta: "low" },
        { label: "Exports", value: "17", delta: "stable" },
      ],
      sections: [
        {
          label: "Tree",
          title: "Filesystem archetype",
          type: "list",
          items: [
            ["/projects/openclaw", "Core platform code and operating docs."],
            ["/projects/rainmaker-ui", "Shell specs, mocks and design tokens."],
            ["/refinery/batches", "Input corpora, extracts and comparison outputs."],
            ["/exports", "Reports, slides, spreadsheets and packaged artifacts."],
          ],
        },
        {
          label: "Preview",
          title: "Selected artifact",
          type: "paragraph",
          text: "The right-hand inspector becomes the preview and action surface. The shell remains identical; the file simply becomes the selected object.",
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "File / rainmaker_console_shell_spec_v1.md",
        facts: [["Kind", "Document"], ["Updated", "Today"], ["Owner", "Leonardo"], ["Actions", "Open · Compare · Export"]],
      },
    },
    Calendar: {
      eyebrow: "Work / Calendar",
      title: "Temporal surface",
      description: "Calendar is not a separate product. It is one operational view inside the shell.",
      status: [{ label: "Sync", value: "Google Calendar" }, { label: "Week", value: "Loaded" }, { label: "Focus", value: "Today" }],
      metrics: [
        { label: "Events", value: "8", delta: "today" },
        { label: "Deep work", value: "4h", delta: "planned" },
        { label: "External", value: "2", delta: "calls" },
        { label: "Agent holds", value: "1", delta: "draft" },
      ],
      sections: [
        {
          label: "Week",
          title: "Temporal grid",
          type: "calendar",
          columns: ["Mon", "Tue", "Wed", "Thu", "Fri"],
          rows: [
            ["Refinery planning", "Psychology", "UI exploration", "Trading review", "Rainmaker shell"],
            ["OpenClaw docs", "Context batch", "Calendar sync", "Design notes", "Component spec"],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Event / Rainmaker shell",
        facts: [["Time", "16:00–18:00"], ["Source", "Google Calendar"], ["Type", "Focus block"], ["Linked project", "Rainmaker UI"]],
      },
    },
    Map: {
      eyebrow: "Work / Map",
      title: "Spatial surface",
      description: "Space and time should fit the same shell grammar.",
      status: [{ label: "Layer", value: "Tasks + routes" }, { label: "Pins", value: "14" }, { label: "Mode", value: "Planning" }],
      metrics: [
        { label: "Regions", value: "3", delta: "tracked" },
        { label: "Travel blocks", value: "2", delta: "today" },
        { label: "Linked tasks", value: "7", delta: "live" },
        { label: "Weather", value: "Clear", delta: "passive" },
      ],
      sections: [
        {
          label: "Surface",
          title: "Spatial board",
          type: "map",
          items: [
            ["Passo Fundo", { x: "28%", y: "45%" }],
            ["São Paulo", { x: "42%", y: "62%" }],
            ["Cloud / EU", { x: "74%", y: "34%" }],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Pin / Passo Fundo",
        facts: [["Linked work", "Calendar + errands"], ["Tasks", "3"], ["State", "Planned"], ["Surface", "Map"]],
      },
    },
  },
  intelligence: {
    Rainmaker: {
      eyebrow: "Intelligence / Rainmaker",
      title: "Agent cockpit",
      description: "The agent gets a cockpit, not a chat box pretending to be an operating system.",
      status: [{ label: "State", value: "Healthy" }, { label: "Attention", value: "Work routing" }, { label: "Memory", value: "Warm" }],
      metrics: [
        { label: "Sessions", value: "5", delta: "active" },
        { label: "Suggested actions", value: "12", delta: "+2" },
        { label: "Recent cost", value: "$18.20", delta: "24h" },
        { label: "Autonomy", value: "Guarded", delta: "manual gates" },
      ],
      sections: [
        {
          label: "Reasoning",
          title: "Current agent posture",
          type: "list",
          items: [
            ["Routing", "Connecting project artifacts to current operational needs."],
            ["Memory", "Maintaining recent context packs close to active tasks."],
            ["Approvals", "Holding changes with cost or risk implications for review."],
          ],
        },
        {
          label: "Outputs",
          title: "Recent suggestions",
          type: "table",
          columns: ["Suggestion", "Target", "Risk", "Action"],
          rows: [
            ["Reorganize design tokens", "Files", "Low", "Review"],
            ["Merge legal excerpts", "Refinery", "Medium", "Approve"],
            ["Pause strategy 03", "Trading", "Medium", "Inspect"],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Agent / Rainmaker",
        facts: [["Role", "Operator agent"], ["Tools", "Files · Runtime · Calendar"], ["Guardrails", "Approval required"], ["Context window", "Expanded"]],
      },
    },
    Refinery: {
      eyebrow: "Intelligence / Refinery",
      title: "Context refinery",
      description: "A builder + review surface for turning raw documents into validated operational context.",
      status: [{ label: "Batches", value: "4 active" }, { label: "Validation", value: "1 pending" }, { label: "Mode", value: "Compare" }],
      metrics: [
        { label: "Sources", value: "128", delta: "loaded" },
        { label: "Extracts", value: "512", delta: "+61" },
        { label: "Candidate merges", value: "14", delta: "review" },
        { label: "Acceptance", value: "82%", delta: "good" },
      ],
      sections: [
        { label: "Flow", title: "Refinery chain", type: "flow", items: ["Ingest", "Extract", "Compare", "Score", "Validate", "Publish"] },
        {
          label: "Diff",
          title: "Current comparison",
          type: "split",
          leftTitle: "Candidate A",
          rightTitle: "Candidate B",
          leftText: "Higher recall, more duplicates, lower semantic precision.",
          rightText: "Lower recall, cleaner merge set, easier validation pass.",
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Batch / legal-corpus-247",
        facts: [["State", "Awaiting validation"], ["Confidence", "0.81"], ["Cost", "$12.14"], ["Next", "Approve publish"]],
      },
    },
    Automations: {
      eyebrow: "Intelligence / Automations",
      title: "Automation builder",
      description: "Flows should feel like composable logic inside the same console grammar.",
      status: [{ label: "Flows", value: "18" }, { label: "Healthy", value: "16" }, { label: "Paused", value: "2" }],
      metrics: [
        { label: "Triggers", value: "29", delta: "live" },
        { label: "Failures", value: "1", delta: "soft" },
        { label: "Retries", value: "3", delta: "automatic" },
        { label: "Avg cost", value: "$0.62", delta: "per run" },
      ],
      sections: [
        { label: "Builder", title: "Flow sketch", type: "flow", items: ["Webhook", "Normalize", "Agent", "Approval", "Export"] },
        {
          label: "Catalogue",
          title: "Reusable nodes",
          type: "list",
          items: [
            ["Calendar trigger", "Listen to event changes and create work items."],
            ["Drive watcher", "Index new artifacts and send them to Files."],
            ["Run gate", "Require approval when cost or risk exceeds threshold."],
          ],
        },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Flow / calendar-to-work",
        facts: [["State", "Healthy"], ["Last run", "4m ago"], ["Success rate", "98.2%"], ["Owner", "Rainmaker"]],
      },
    },
    Memory: {
      eyebrow: "Intelligence / Memory",
      title: "Memory surface",
      description: "Memory becomes an inspectable asset: context packs, links and recency, not mystery fog.",
      status: [{ label: "Hot packs", value: "11" }, { label: "Archives", value: "204" }, { label: "Mode", value: "Inspectable" }],
      metrics: [
        { label: "Linked entities", value: "346", delta: "graph" },
        { label: "Recent recalls", value: "28", delta: "24h" },
        { label: "Drift alerts", value: "2", delta: "soft" },
        { label: "Index age", value: "12m", delta: "fresh" },
      ],
      sections: [{ label: "Graph", title: "Memory neighborhoods", type: "bars", items: [["OpenClaw", 81], ["Rainmaker UI", 64], ["Refinery", 72], ["Trading", 49], ["Calendar", 21]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Context pack / rainmaker-ui",
        facts: [["State", "Hot"], ["Size", "22 linked notes"], ["Last recall", "9m ago"], ["Confidence", "High"]],
      },
    },
  },
  runtime: {
    Runs: {
      eyebrow: "Runtime / Runs",
      title: "Execution field",
      description: "Runs deserve their own calm live-console surface inside the same shell.",
      status: [{ label: "Running", value: "12" }, { label: "Queued", value: "7" }, { label: "Failed", value: "1 soft" }],
      metrics: [
        { label: "Throughput", value: "84 tasks/h", delta: "+7" },
        { label: "Avg duration", value: "6m 12s", delta: "steady" },
        { label: "Compute", value: "63%", delta: "nominal" },
        { label: "Cloud cost", value: "$14.90", delta: "session" },
      ],
      sections: [
        {
          label: "Runs",
          title: "Active executions",
          type: "table",
          columns: ["Run", "Target", "State", "Duration"],
          rows: [["#2471", "Refinery compare", "Running", "04:18"], ["#2470", "Trading replay", "Running", "16:42"], ["#2468", "Drive index", "Queued", "--"]],
        },
        { label: "Events", title: "Run feed", type: "timeline", items: [["#2471", "Validation checkpoint reached."], ["#2470", "PnL summary artifact exported."], ["#2468", "Waiting for OCR worker slot."]] },
      ],
      inspector: {
        title: "Selected object",
        subtitle: "Run / #2471",
        facts: [["State", "Running"], ["Started", "16:13"], ["Cost", "$2.18"], ["Artifacts", "3 generated"]],
      },
    },
    Queues: {
      eyebrow: "Runtime / Queues",
      title: "Queue architecture",
      description: "Queues are first-class surfaces because execution pressure is part of operational awareness.",
      status: [{ label: "Depth", value: "7" }, { label: "Pressure", value: "Low" }, { label: "Workers", value: "11" }],
      metrics: [{ label: "OCR", value: "2", delta: "waiting" }, { label: "Agent jobs", value: "1", delta: "ready" }, { label: "Exports", value: "3", delta: "normal" }, { label: "Backfill", value: "1", delta: "paused" }],
      sections: [{ label: "Distribution", title: "Queue composition", type: "bars", items: [["OCR", 22], ["Agent", 14], ["Exports", 29], ["Index", 36]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Queue / index",
        facts: [["State", "Healthy"], ["Depth", "3"], ["Workers", "4"], ["Retry policy", "Automatic"]],
      },
    },
    Logs: {
      eyebrow: "Runtime / Logs",
      title: "Log surface",
      description: "Dense information remains readable because the shell stays stable and the typography does the work.",
      status: [{ label: "Verbosity", value: "Operational" }, { label: "Filter", value: "Warnings" }, { label: "Window", value: "1h" }],
      metrics: [{ label: "Entries", value: "1,842", delta: "1h" }, { label: "Warnings", value: "17", delta: "visible" }, { label: "Errors", value: "1", delta: "soft" }, { label: "Noise", value: "Low" }],
      sections: [{ label: "Feed", title: "Recent log entries", type: "loglines", items: ["16:27:12  WARN   drive.index  retry scheduled after rate limit", "16:26:40  INFO   gateway.ws   client synced with runtime backbone", "16:24:09  INFO   agent.route  recommendation emitted to approval lane", "16:22:51  WARN   finance.burn soft threshold crossed then normalized"] }],
      inspector: {
        title: "Selected object",
        subtitle: "Log / drive.index",
        facts: [["Level", "Warn"], ["Cause", "Rate limit"], ["Recovery", "Automatic retry"], ["Impact", "Low"]],
      },
    },
    Approvals: {
      eyebrow: "Runtime / Approvals",
      title: "Approval lane",
      description: "All guarded autonomy converges here as a review surface, not as hidden modal popups.",
      status: [{ label: "Pending", value: "3" }, { label: "High risk", value: "1" }, { label: "Auto-approved", value: "19" }],
      metrics: [{ label: "Avg decision", value: "11m" }, { label: "Manual gates", value: "4" }, { label: "Cost deltas", value: "2" }, { label: "Rejected", value: "1" }],
      sections: [{ label: "Review", title: "Pending decisions", type: "table", columns: ["Item", "Area", "Risk", "Decision"], rows: [["Trading config delta", "Runtime", "High", "Pending"], ["Context merge / legal", "Refinery", "Medium", "Pending"], ["Folder reorg", "Files", "Low", "Pending"]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Approval / context merge",
        facts: [["State", "Pending"], ["Risk", "Medium"], ["Estimated cost", "$1.94"], ["Requester", "Rainmaker"]],
      },
    },
  },
  finance: {
    Spend: {
      eyebrow: "Finance / Spend",
      title: "Cost field",
      description: "Cost is part of the shell, visible globally, live and per object.",
      status: [{ label: "Month", value: "$428.10" }, { label: "Trend", value: "+6.2%" }, { label: "Alerts", value: "2 soft" }],
      metrics: [{ label: "Agents", value: "$182" }, { label: "Cloud", value: "$143" }, { label: "Storage", value: "$41" }, { label: "Exports", value: "$19" }],
      sections: [{ label: "Breakdown", title: "Spend by area", type: "bars", items: [["Agents", 66], ["Cloud", 58], ["Storage", 22], ["Exports", 14], ["Calendar", 8]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Cost center / agents",
        facts: [["State", "Healthy"], ["Month to date", "$182"], ["Most expensive", "Rainmaker"], ["Action", "Inspect breakdown"]],
      },
    },
    Burn: {
      eyebrow: "Finance / Burn",
      title: "Burn-rate line",
      description: "The shell should reveal speed, not only totals.",
      status: [{ label: "Current", value: "$7.12 / h" }, { label: "Expected", value: "$6.80 / h" }, { label: "Gap", value: "+4.7%" }],
      metrics: [{ label: "Agents", value: "$3.24 / h" }, { label: "Compute", value: "$2.98 / h" }, { label: "Storage", value: "$0.21 / h" }, { label: "Misc", value: "$0.69 / h" }],
      sections: [{ label: "Trace", title: "Hourly profile", type: "bars", items: [["09:00", 34], ["11:00", 42], ["13:00", 39], ["15:00", 51], ["17:00", 46]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Burn / current hour",
        facts: [["State", "Within soft bounds"], ["Primary driver", "Compute"], ["Compared to avg", "+4.7%"], ["Recommendation", "Monitor"]],
      },
    },
    Forecast: {
      eyebrow: "Finance / Forecast",
      title: "Projection surface",
      description: "Forecasts belong near operation because decisions create cost.",
      status: [{ label: "Month end", value: "$471" }, { label: "Confidence", value: "0.78" }, { label: "Scenarios", value: "3" }],
      metrics: [{ label: "Base", value: "$459" }, { label: "High", value: "$518" }, { label: "Low", value: "$432" }, { label: "Delta drivers", value: "Compute + agents" }],
      sections: [{ label: "Scenarios", title: "Projection bands", type: "split", leftTitle: "Conservative", rightTitle: "Aggressive", leftText: "Maintain current activity with moderate refinement and review load.", rightText: "Increase automation density and run extended trading replays." }],
      inspector: {
        title: "Selected object",
        subtitle: "Forecast / base case",
        facts: [["State", "Stable"], ["Confidence", "0.78"], ["Main risk", "Compute spikes"], ["Suggested action", "Cap overnight runs"]],
      },
    },
    Anomalies: {
      eyebrow: "Finance / Anomalies",
      title: "Cost anomaly lane",
      description: "Finance needs the same review grammar as runtime and approvals.",
      status: [{ label: "Open", value: "2" }, { label: "Resolved", value: "5" }, { label: "Severity", value: "Soft" }],
      metrics: [{ label: "Detection", value: "18m" }, { label: "False positives", value: "Low" }, { label: "Largest spike", value: "+11%" }, { label: "Impact", value: "$9.40" }],
      sections: [{ label: "Cases", title: "Recent anomalies", type: "table", columns: ["Case", "Area", "Delta", "State"], rows: [["Overnight compute", "Trading", "+11%", "Review"], ["Duplicate export", "Artifacts", "+3%", "Resolved"], ["Agent retries", "Rainmaker", "+2%", "Observed"]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Anomaly / overnight compute",
        facts: [["State", "Review"], ["Cause", "Trading replay burst"], ["Impact", "$9.40"], ["Suggested action", "Throttle queue"]],
      },
    },
  },
  system: {
    Integrations: {
      eyebrow: "System / Integrations",
      title: "Integration control",
      description: "Setup lives here, but the effects of integration appear everywhere else in the shell.",
      status: [{ label: "Connected", value: "8" }, { label: "Warnings", value: "1" }, { label: "Gateway", value: "Primary" }],
      metrics: [{ label: "Google Calendar", value: "Healthy" }, { label: "Google Drive", value: "Healthy" }, { label: "Cloud storage", value: "Healthy" }, { label: "Email", value: "Degraded" }],
      sections: [{ label: "Registry", title: "Connected systems", type: "table", columns: ["System", "Mode", "Health", "Scope"], rows: [["OpenClaw", "Gateway", "Healthy", "Global"], ["Google Calendar", "Webhook", "Healthy", "Work"], ["Google Drive", "Sync", "Healthy", "Files"], ["Email", "Polling", "Degraded", "System"]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Integration / Google Calendar",
        facts: [["State", "Healthy"], ["Sync age", "2m"], ["Surfaces", "Work · Runtime"], ["Action", "Re-auth · Inspect logs"]],
      },
    },
    Environments: {
      eyebrow: "System / Environments",
      title: "Environment topology",
      description: "Local, cloud, sandbox and production remain legible at all times from the shell.",
      status: [{ label: "Local", value: "Online" }, { label: "Cloud", value: "Primary" }, { label: "Prod", value: "Guarded" }],
      metrics: [{ label: "Local jobs", value: "2" }, { label: "Cloud jobs", value: "12" }, { label: "Prod gates", value: "4" }, { label: "Sandbox", value: "Idle" }],
      sections: [{ label: "Topology", title: "Environment lanes", type: "flow", items: ["Local", "Sandbox", "Cloud", "Production"] }],
      inspector: {
        title: "Selected object",
        subtitle: "Environment / cloud",
        facts: [["Role", "Primary execution"], ["State", "Healthy"], ["Jobs", "12"], ["Guardrails", "Approval on prod-facing changes"]],
      },
    },
    Observability: {
      eyebrow: "System / Observability",
      title: "Observability shell",
      description: "Health, telemetry and audit trails should use the same visual grammar as the rest of the console.",
      status: [{ label: "Health", value: "Good" }, { label: "Alerts", value: "2 soft" }, { label: "Audit", value: "Continuous" }],
      metrics: [{ label: "Gateway", value: "Healthy" }, { label: "Workers", value: "11 online" }, { label: "Web clients", value: "3" }, { label: "Incident risk", value: "Low" }],
      sections: [{ label: "Health", title: "Subsystem traces", type: "bars", items: [["Gateway", 84], ["Workers", 78], ["Storage", 73], ["Integrations", 69], ["Exports", 61]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Subsystem / gateway",
        facts: [["State", "Healthy"], ["Heartbeat", "Stable"], ["Clients", "3"], ["Transport", "WebSocket"]],
      },
    },
    Access: {
      eyebrow: "System / Access",
      title: "Access and trust",
      description: "Access should be inspectable, explicit and structurally calm.",
      status: [{ label: "Profiles", value: "4" }, { label: "Critical scopes", value: "3" }, { label: "Audit", value: "Enabled" }],
      metrics: [{ label: "Operator", value: "Full" }, { label: "Agent", value: "Guarded" }, { label: "Automation", value: "Scoped" }, { label: "Guests", value: "0" }],
      sections: [{ label: "Access map", title: "Role surfaces", type: "list", items: [["Operator", "Human oversight over all key surfaces."], ["Rainmaker agent", "Broad read access, guarded write actions."], ["Automations", "Narrow scopes and explicit trigger paths."]] }],
      inspector: {
        title: "Selected object",
        subtitle: "Role / Rainmaker agent",
        facts: [["Read", "Broad"], ["Write", "Guarded"], ["Escalation", "Approval lane"], ["Audit trail", "Complete"]],
      },
    },
  },
};

const DOMAINS = resolveDomains(ICON_REGISTRY, TOKENS);
const RUNTIME_ITEMS = resolveRuntimeItems(TOKENS);

function cx(...parts) {
  return parts.filter(Boolean).join(" ");
}

function useVirtualViewportArea() {
  const [viewport, setViewport] = useState({ width: 1440, height: 900 });

  useEffect(() => {
    const syncViewport = () => {
      startTransition(() => {
        setViewport({
          width: window.innerWidth,
          height: window.innerHeight,
        });
      });
    };

    syncViewport();
    window.addEventListener("resize", syncViewport);
    return () => window.removeEventListener("resize", syncViewport);
  }, []);

  return viewport;
}

function getMetricMeta(delta, accent) {
  if (!delta) {
    return { tone: TOKENS.ink3, fill: TOKENS.bg1, border: TOKENS.line };
  }

  const value = String(delta).trim();
  const looksNumericDelta = /^[+-]/.test(value);
  const looksTime = /(?:h|m|d|wk|mo|yr)$/i.test(value);

  if (looksNumericDelta) {
    return { tone: accent || TOKENS.ink1, fill: TOKENS.bg0, border: accent || TOKENS.line };
  }

  if (looksTime) {
    return { tone: TOKENS.ink2, fill: TOKENS.bg0, border: TOKENS.line };
  }

  return { tone: TOKENS.ink2, fill: TOKENS.bg0, border: TOKENS.line };
}

function Metric({ label, value, delta, accent }) {
  const meta = getMetricMeta(delta, accent);

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 320, damping: 24 }}
      className="min-w-0 rounded-2xl border p-4 lg:rounded-none lg:border-0 lg:border-r lg:bg-transparent lg:p-0 lg:pr-6 lg:last:border-r-0 lg:last:pr-0"
      style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}
    >
      <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>
        {label}
      </div>

      <div className="mt-3 flex items-end justify-between gap-3">
        <div className="min-w-0 truncate text-[clamp(1.125rem,2.4vw,1.5rem)] font-semibold tracking-[-0.02em] tabular-nums" style={{ color: TOKENS.ink0 }}>
          {value}
        </div>

        {delta ? (
          <div
            className="shrink-0 rounded-full border px-2.5 py-1 text-[10px] uppercase tracking-[0.16em]"
            style={{ color: meta.tone, background: meta.fill, borderColor: meta.border }}
          >
            {delta}
          </div>
        ) : null}
      </div>
    </motion.div>
  );
}

function Section({ label, title, children, tint }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="grid gap-4 py-5 first:pt-0"
      style={{ borderTop: `1px solid ${TOKENS.line}` }}
    >
      <div className="flex items-end justify-between gap-6">
        <div className="grid gap-1">
          <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>{label}</div>
          <h3 className="text-base font-semibold tracking-tight" style={{ color: TOKENS.ink0 }}>{title}</h3>
        </div>
        <div className="h-px flex-1" style={{ background: tint, opacity: 0.5 }} />
      </div>
      {children}
    </motion.section>
  );
}

function ScreenSection({ section, tint }) {
  if (section.type === "list") {
    return (
      <div className="grid gap-3">
        {section.items.map(([title, body]) => (
          <div key={title} className="grid gap-1.5">
            <div className="text-sm font-medium" style={{ color: TOKENS.ink1 }}>{title}</div>
            <div className="max-w-3xl text-sm leading-6" style={{ color: TOKENS.ink2 }}>{body}</div>
          </div>
        ))}
      </div>
    );
  }

  if (section.type === "timeline") {
    return (
      <div className="grid gap-3">
        {section.items.map(([time, body], index) => (
          <div key={`${time}-${index}`} className="grid grid-cols-1 gap-1 text-sm sm:grid-cols-[96px_1fr] sm:gap-4">
            <div className="font-mono" style={{ color: TOKENS.ink3 }}>{time}</div>
            <div className="leading-6" style={{ color: TOKENS.ink1 }}>{body}</div>
          </div>
        ))}
      </div>
    );
  }

  if (section.type === "table") {
    return (
      <div className="overflow-x-auto rounded-xl border" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
        <div className="min-w-[560px]">
          <div className="grid text-[10px] uppercase tracking-[0.22em]" style={{ gridTemplateColumns: `repeat(${section.columns.length}, minmax(0, 1fr))`, color: TOKENS.ink3 }}>
            {section.columns.map((column) => (
              <div key={column} className="border-b px-4 py-3" style={{ borderColor: TOKENS.line }}>{column}</div>
            ))}
          </div>
          {section.rows.map((row, i) => (
            <div key={i} className="grid text-sm" style={{ gridTemplateColumns: `repeat(${row.length}, minmax(0, 1fr))` }}>
              {row.map((cell, j) => (
                <div key={`${i}-${j}`} className="border-b px-4 py-3 last:border-b-0" style={{ borderColor: TOKENS.line, color: TOKENS.ink1 }}>{cell}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (section.type === "paragraph") {
    return <p className="max-w-3xl text-sm leading-7" style={{ color: TOKENS.ink2 }}>{section.text}</p>;
  }

  if (section.type === "bars") {
    return (
      <div className="grid gap-3">
        {section.items.map(([label, value]) => (
          <div key={label} className="grid grid-cols-[96px_1fr_48px] items-center gap-3 sm:grid-cols-[120px_1fr_56px] sm:gap-4">
            <div className="text-sm" style={{ color: TOKENS.ink2 }}>{label}</div>
            <div className="h-2 overflow-hidden rounded-full" style={{ background: TOKENS.bg2 }}>
              <motion.div
                className="h-full rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                style={{ background: tint }}
              />
            </div>
            <div className="text-right font-mono text-xs" style={{ color: TOKENS.ink3 }}>{value}</div>
          </div>
        ))}
      </div>
    );
  }

  if (section.type === "flow") {
    return (
      <div className="flex flex-wrap gap-3">
        {section.items.map((item, index) => (
          <React.Fragment key={item}>
            <div className="rounded-full border px-4 py-2 text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>{item}</div>
            {index < section.items.length - 1 ? <ArrowGlyph className="mt-2 h-4 w-4" style={{ color: TOKENS.ink3 }} /> : null}
          </React.Fragment>
        ))}
      </div>
    );
  }

  if (section.type === "split") {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border p-5" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
          <div className="mb-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>{section.leftTitle}</div>
          <div className="text-sm leading-7" style={{ color: TOKENS.ink2 }}>{section.leftText}</div>
        </div>
        <div className="rounded-2xl border p-5" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
          <div className="mb-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>{section.rightTitle}</div>
          <div className="text-sm leading-7" style={{ color: TOKENS.ink2 }}>{section.rightText}</div>
        </div>
      </div>
    );
  }

  if (section.type === "calendar") {
    return (
      <div className="overflow-x-auto rounded-2xl border" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
        <div className="min-w-[720px]">
          <div className="grid" style={{ gridTemplateColumns: `repeat(${section.columns.length}, minmax(0, 1fr))` }}>
            {section.columns.map((column) => (
              <div key={column} className="border-b px-4 py-3 text-[10px] uppercase tracking-[0.22em]" style={{ borderColor: TOKENS.line, color: TOKENS.ink3 }}>{column}</div>
            ))}
          </div>
          {section.rows.map((row, i) => (
            <div key={i} className="grid" style={{ gridTemplateColumns: `repeat(${row.length}, minmax(0, 1fr))` }}>
              {row.map((cell, j) => (
                <div key={`${i}-${j}`} className="min-h-[86px] border-b px-4 py-3 text-sm leading-6" style={{ borderColor: TOKENS.line, color: TOKENS.ink1 }}>{cell}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (section.type === "map") {
    return (
      <div className="relative min-h-[var(--map-min-h)] overflow-hidden rounded-[var(--surface-radius)] border" style={{ borderColor: TOKENS.line, background: `linear-gradient(180deg, ${TOKENS.bg1} 0%, ${TOKENS.bg0} 100%)` }}>
        <div className="absolute inset-0 opacity-60" style={{ backgroundImage: `linear-gradient(${TOKENS.line} 1px, transparent 1px), linear-gradient(90deg, ${TOKENS.line} 1px, transparent 1px)`, backgroundSize: "var(--map-grid-size) var(--map-grid-size)" }} />
        {section.items.map(([label, pos]) => (
          <motion.div
            key={label}
            className="absolute flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs"
            style={{ left: pos.x, top: pos.y, transform: "translate(-50%, -50%)", borderColor: tint, background: TOKENS.bg0, color: TOKENS.ink1 }}
            animate={{ scale: [1, 1.03, 1] }}
            transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}
          >
            <span className="h-2 w-2 rounded-full" style={{ background: tint }} />
            {label}
          </motion.div>
        ))}
      </div>
    );
  }

  if (section.type === "loglines") {
    return (
      <div className="overflow-hidden rounded-2xl border" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
        {section.items.map((line, i) => (
          <div key={i} className="border-b px-4 py-3 font-mono text-xs leading-6 last:border-b-0" style={{ borderColor: TOKENS.line, color: TOKENS.ink1 }}>{line}</div>
        ))}
      </div>
    );
  }

  return null;
}

function StatusPill({ label, value, soft, tint }) {
  return (
    <motion.div
      whileHover={{ y: -1.5, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 360, damping: 26 }}
      className="rounded-full border px-3 py-2"
      style={{ borderColor: tint, background: soft }}
    >
      <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>{label}</div>
      <div className="text-sm font-medium" style={{ color: TOKENS.ink1 }}>{value}</div>
    </motion.div>
  );
}

function ConfigWarning({ errors }) {
  if (!errors.length) return null;

  return (
    <div className="rounded-2xl border p-4 text-sm" style={{ borderColor: TOKENS.red, background: TOKENS.redSoft, color: TOKENS.ink1 }}>
      <div className="mb-2 text-[10px] uppercase tracking-[0.22em]">Config warnings</div>
      <ul className="grid gap-1">
        {errors.map((error) => (
          <li key={error}>• {error}</li>
        ))}
      </ul>
    </div>
  );
}

export default function RainmakerConsoleUIPrototype() {
  const [domainId, setDomainId] = useState("intelligence");
  const [node, setNode] = useState("Rainmaker");
  const [commandOpen, setCommandOpen] = useState(false);
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [themeId, setThemeId] = useState("paper");

  const viewport = useVirtualViewportArea();
  const domain = useMemo(() => DOMAINS.find((item) => item.id === domainId) || DOMAINS[0], [domainId]);
  const screenGroup = SCREENS[domain.id] || {};
  const safeNode = screenGroup[node] ? node : domain.nodes[0];
  const screen = screenGroup[safeNode];
  const theme = resolveTheme(themeId);
  const themeVars = useMemo(() => createThemeCssVars(theme), [theme]);
  const layoutVars = useMemo(() => deriveLayoutVars(viewport), [viewport]);
  const configErrors = useMemo(() => validateDomainScreens(DOMAINS, SCREENS), []);

  useEffect(() => {
    const onKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen((value) => !value);
      }
      if (event.key === "Escape") {
        setCommandOpen(false);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    if (configErrors.length) {
      console.warn("Rainmaker Console config warnings:", configErrors);
    }
  }, [configErrors]);

  const handleSelectDomain = (id) => {
    const next = DOMAINS.find((item) => item.id === id) || DOMAINS[0];
    setDomainId(next.id);
    setNode(next.nodes[0]);
  };

  const jumpTo = (nextDomainId, nextNode) => {
    const next = DOMAINS.find((item) => item.id === nextDomainId) || DOMAINS[0];
    setDomainId(next.id);
    setNode(nextNode || next.nodes[0]);
    setCommandOpen(false);
  };

  return (
    <div
      className="min-h-screen w-full p-3 sm:p-4 lg:p-6"
      style={{
        ...themeVars,
        ...layoutVars,
        background: TOKENS.bg2,
        color: TOKENS.ink0,
      }}
    >
      <div
        className={cx(
          "relative mx-auto grid h-auto min-h-[var(--shell-min-h)] max-w-[var(--shell-max-w)] overflow-hidden rounded-[var(--shell-radius)] border lg:h-[var(--shell-min-h)]",
          "grid-cols-1 grid-rows-[auto_auto_auto_minmax(0,1fr)_auto_auto]",
          SHELL_GRID_ROW_CLASS,
          resolveShellColumnClass(sidebarOpen, inspectorOpen)
        )}
        style={{ background: TOKENS.bg0, borderColor: TOKENS.line, boxShadow: `0 24px 80px ${TOKENS.shadow}` }}
      >
        <motion.div
          aria-hidden
          className="pointer-events-none absolute -left-20 top-12 h-64 w-64 rounded-full blur-3xl"
          style={{ background: domain.soft, opacity: 0.45 }}
          animate={{ x: [0, 16, -8, 0], y: [0, -12, 8, 0], scale: [1, 1.06, 0.98, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          aria-hidden
          className="pointer-events-none absolute right-[-72px] top-[-48px] h-72 w-72 rounded-full blur-3xl"
          style={{ background: TOKENS.blueSoft, opacity: 0.25 }}
          animate={{ x: [0, -14, 8, 0], y: [0, 12, -10, 0], scale: [1, 0.98, 1.05, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        />

        <header
          className="grid grid-cols-1 gap-3 border-b px-3 py-3 sm:px-4 lg:grid-cols-[var(--brand-w)_minmax(0,1fr)_minmax(var(--toolbar-min),auto)] lg:items-center lg:py-0"
          style={{ gridColumn: "1 / -1", borderColor: TOKENS.line, background: TOKENS.bg0, minHeight: "var(--header-h)" }}
        >
          <div className="flex items-center gap-3 pl-1">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl border" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
              <MarkGlyph className="h-4 w-4" />
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-[0.24em]" style={{ color: TOKENS.ink3 }}>Workspace</div>
              <div className="text-sm font-semibold tracking-tight">Rainmaker Console</div>
            </div>
          </div>

          <div className="px-4">
            <button
              onClick={() => setCommandOpen(true)}
              className="flex h-10 w-full items-center gap-3 rounded-full border px-4 text-left"
              style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}
            >
              <SearchGlyph className="h-4 w-4" style={{ color: TOKENS.ink3 }} />
              <span className="text-sm" style={{ color: TOKENS.ink3 }}>Command, search, route, inspect...</span>
              <span className="ml-auto rounded-full border px-2 py-1 text-[10px] uppercase tracking-[0.18em]" style={{ borderColor: TOKENS.line, color: TOKENS.ink3 }}>Cmd+K</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center justify-end gap-2 pr-1 lg:gap-3">
            <div className="rounded-full border px-3 py-2 text-xs font-medium" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>cloud / primary</div>
            <div className="rounded-full border px-3 py-2 text-xs font-medium" style={{ borderColor: TOKENS.line, background: domain.soft, color: domain.tint }}>sync / live</div>
            <div className="flex items-center gap-1 rounded-full border p-1" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
              {THEME_CHOICES.map((item) => {
                const Icon = item.icon;
                const active = item.id === themeId;
                return (
                  <motion.button
                    key={item.id}
                    whileHover={{ y: -1 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => setThemeId(item.id)}
                    title={item.label}
                    className="flex h-8 w-8 items-center justify-center rounded-full border"
                    style={{ borderColor: active ? domain.tint : "transparent", background: active ? domain.soft : "transparent", color: active ? domain.tint : TOKENS.ink2 }}
                  >
                    <Icon className="h-4 w-4" />
                  </motion.button>
                );
              })}
            </div>
            <button onClick={() => setSidebarOpen((value) => !value)} className="rounded-full border px-3 py-2 text-xs font-medium" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink2 }}>
              {sidebarOpen ? "hide sidebar" : "show sidebar"}
            </button>
            <button onClick={() => setInspectorOpen((value) => !value)} className="rounded-full border px-3 py-2 text-xs font-medium" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink2 }}>
              {inspectorOpen ? "hide inspector" : "show inspector"}
            </button>
            <button className="flex h-10 w-10 items-center justify-center rounded-full border" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
              <BellGlyph className="h-4 w-4" />
            </button>
          </div>
        </header>

        {sidebarOpen ? (
          <>
            <aside className="border-b py-4 lg:row-start-2 lg:border-b-0 lg:border-r" style={{ borderColor: TOKENS.line, background: TOKENS.bg0 }}>
              <div className="flex flex-row items-center gap-2 overflow-x-auto px-3 lg:h-full lg:flex-col lg:items-center lg:px-0">
                <div className="mb-1 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Nav</div>
                {DOMAINS.map((item) => {
                  const Icon = item.icon;
                  const active = item.id === domain.id;
                  return (
                    <button key={item.id} title={item.label} onClick={() => handleSelectDomain(item.id)} className="relative flex items-center justify-center rounded-2xl px-2 py-2.5 transition-all" style={{ color: active ? item.tint : TOKENS.ink2 }}>
                      {active ? <span className="absolute left-0 top-1/2 h-8 w-[2px] -translate-y-1/2 rounded-full" style={{ background: item.tint }} /> : null}
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl" style={{ background: active ? item.soft : "transparent", border: `1px solid ${active ? item.tint : "transparent"}` }}>
                        <Icon className="h-4 w-4" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </aside>

            <aside className="border-b px-4 py-5 sm:px-6 lg:row-start-2 lg:border-b-0 lg:border-r" style={{ borderColor: TOKENS.line, background: TOKENS.bg0 }}>
              <div className="grid h-full grid-rows-[auto_auto_1fr] gap-6">
                <div className="grid gap-2 border-b pb-4" style={{ borderColor: TOKENS.line }}>
                  <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Plane</div>
                  <div className="text-[clamp(1.125rem,2.4vw,1.375rem)] font-semibold tracking-[-0.02em]" style={{ color: TOKENS.ink0 }}>{domain.label}</div>
                  <p className="max-w-[22ch] text-sm leading-6" style={{ color: TOKENS.ink2 }}>Stable structure. Variable view.</p>
                </div>

                <div className="grid gap-1.5">
                  <div className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>
                    <TreeGlyph className="h-3.5 w-3.5" style={{ color: domain.tint }} />
                    Context
                  </div>
                  {domain.nodes.map((item) => {
                    const active = item === safeNode;
                    return (
                      <button key={item} onClick={() => setNode(item)} className="group relative flex items-center justify-between border-b py-3 text-left text-sm transition-all" style={{ borderColor: TOKENS.line, color: active ? TOKENS.ink0 : TOKENS.ink2 }}>
                        <div className="flex items-center gap-3">
                          <span className="h-5 w-[2px] rounded-full" style={{ background: active ? domain.tint : "transparent" }} />
                          <span className="font-medium">{item}</span>
                        </div>
                        <ArrowGlyph className="h-4 w-4" style={{ color: active ? domain.tint : TOKENS.ink3 }} />
                      </button>
                    );
                  })}
                </div>

                <div className="mt-auto grid gap-3 border-t pt-4" style={{ borderColor: TOKENS.line }}>
                  <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Grammar</div>
                  <p className="text-sm leading-7" style={{ color: TOKENS.ink2 }}>The shell does not morph. Only the selected object and view change.</p>
                  <div className="grid gap-1 text-xs" style={{ color: TOKENS.ink3 }}>
                    <div>Plane / Collection / Object / View</div>
                    <div>Explorer / Cockpit / Live / Builder / Review</div>
                  </div>
                </div>
              </div>
            </aside>
          </>
        ) : null}

        <main className="min-w-0 overflow-hidden lg:row-start-2" style={{ background: TOKENS.bg0 }}>
          <AnimatePresence mode="wait">
            <motion.div key={`${domain.id}-${safeNode}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }} className="grid h-full grid-rows-[auto_auto_1fr]">
              <div className="border-b px-4 py-5 sm:px-6 lg:px-8 lg:py-6" style={{ borderColor: TOKENS.line }}>
                <div className="mb-3 flex items-center gap-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}><span>{screen.eyebrow}</span></div>
                <div className="flex flex-wrap items-end justify-between gap-6">
                  <div className="max-w-3xl">
                    <h1 className="text-[clamp(1.75rem,3vw,2rem)] font-semibold tracking-[-0.03em]" style={{ color: TOKENS.ink0 }}>{screen.title}</h1>
                    <p className="mt-3 max-w-3xl text-sm leading-7" style={{ color: TOKENS.ink2 }}>{screen.description}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button className="rounded-full border px-4 py-2 text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>Overview</button>
                    <button className="rounded-full border px-4 py-2 text-sm" style={{ borderColor: domain.tint, background: domain.soft, color: domain.tint }}>Primary action</button>
                  </div>
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  {screen.status.map((item) => <StatusPill key={item.label} label={item.label} value={item.value} soft={domain.soft} tint={domain.tint} />)}
                </div>
              </div>

              <div className="border-b px-4 py-4 sm:px-6 lg:px-8 lg:py-5" style={{ borderColor: TOKENS.line }}>
                <div className="grid gap-3 [grid-template-columns:repeat(auto-fit,minmax(140px,1fr))] lg:flex lg:min-w-max lg:gap-6">
                  {screen.metrics.map((metric) => <Metric key={metric.label} {...metric} accent={domain.tint} />)}
                </div>
              </div>

              <div className="overflow-y-auto px-4 py-5 sm:px-6 lg:px-8 lg:py-6">
                <div className="grid gap-7">
                  <ConfigWarning errors={configErrors} />
                  {screen.sections.map((section) => (
                    <Section key={`${section.label}-${section.title}`} label={section.label} title={section.title} tint={domain.tint}>
                      <ScreenSection section={section} tint={domain.tint} />
                    </Section>
                  ))}
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </main>

        {inspectorOpen ? (
          <aside className="overflow-hidden border-t p-4 sm:p-5 lg:row-start-2 lg:border-l lg:border-t-0" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
            <div className="grid h-full grid-rows-[auto_auto_1fr_auto] gap-5">
              <div className="grid gap-1">
                <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Inspector</div>
                <div className="text-lg font-semibold tracking-tight">{screen.inspector.title}</div>
              </div>

              <div className="rounded-[var(--panel-radius)] border p-4" style={{ borderColor: TOKENS.line, background: TOKENS.bg0 }}>
                <div className="mb-1 text-sm font-medium" style={{ color: TOKENS.ink1 }}>{screen.inspector.subtitle}</div>
                <div className="text-xs leading-6" style={{ color: TOKENS.ink3 }}>Context, relations, cost and action live here.</div>
              </div>

              <div className="rounded-[var(--panel-radius)] border p-4" style={{ borderColor: TOKENS.line, background: TOKENS.bg0 }}>
                <div className="mb-4 flex items-center gap-2 text-sm font-medium" style={{ color: TOKENS.ink1 }}>
                  {domain.id === "work" ? <StorageGlyph className="h-4 w-4" /> : null}
                  {domain.id === "intelligence" ? <AgentGlyph className="h-4 w-4" /> : null}
                  {domain.id === "runtime" ? <RuntimeGlyph className="h-4 w-4" /> : null}
                  {domain.id === "finance" ? <FinanceGlyph className="h-4 w-4" /> : null}
                  {domain.id === "system" ? <GuardGlyph className="h-4 w-4" /> : null}
                  {domain.id === "overview" ? <CloudGlyph className="h-4 w-4" /> : null}
                  Object facts
                </div>
                <div className="grid gap-3">
                  {screen.inspector.facts.map(([label, value]) => (
                    <div key={label} className="grid grid-cols-[72px_1fr] gap-3 text-sm sm:grid-cols-[88px_1fr]">
                      <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>{label}</div>
                      <div style={{ color: TOKENS.ink1 }}>{value}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-[var(--panel-radius)] border p-4" style={{ borderColor: TOKENS.line, background: domain.soft }}>
                <div className="mb-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Actions</div>
                <div className="grid gap-2">
                  {["Inspect relations", "Open audit trail", "Compare state", "Export snapshot"].map((action) => (
                    <button key={action} className="rounded-full border px-3 py-2 text-left text-sm" style={{ borderColor: domain.tint, color: domain.tint, background: TOKENS.bg0 }}>{action}</button>
                  ))}
                </div>
              </div>
            </div>
          </aside>
        ) : null}

        <footer className="flex flex-wrap items-center gap-2 border-t px-3 py-2 lg:py-0" style={{ gridColumn: "1 / -1", borderColor: TOKENS.line, background: TOKENS.bg0, minHeight: "var(--footer-h)" }}>
          <div className="mr-2 text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Runtime strip</div>
          <div className="flex min-w-0 flex-1 flex-wrap gap-2 overflow-x-auto pb-1 pt-1 lg:flex-nowrap">
            {RUNTIME_ITEMS.map((item) => (
              <motion.div key={item.label} className="flex min-w-[140px] flex-1 items-center justify-between rounded-full border px-3 py-2 text-xs sm:min-w-[176px] lg:flex-none" style={{ borderColor: item.ink, background: item.tone }} animate={{ y: [0, -1.5, 0] }} transition={{ duration: 3.6, repeat: Infinity, ease: "easeInOut" }}>
                <span className="truncate pr-3" style={{ color: TOKENS.ink1 }}>{item.label}</span>
                <span className="font-medium" style={{ color: item.ink }}>{item.state}</span>
              </motion.div>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-2 pl-2 text-xs" style={{ color: TOKENS.ink3 }}>
            <CalendarGlyph className="h-4 w-4" />
            <MapGlyph className="h-4 w-4" />
            <FlowGlyph className="h-4 w-4" />
            <StackGlyph className="h-4 w-4" />
            <BoltGlyph className="h-4 w-4" />
          </div>
        </footer>

        <AnimatePresence>
          {commandOpen ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-50 flex items-start justify-center backdrop-blur-sm" style={{ padding: "var(--command-overlay-pad)", background: TOKENS.overlay }}>
              <motion.div initial={{ opacity: 0, y: 14, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -8, scale: 0.99 }} transition={{ duration: 0.16 }} className="w-full overflow-hidden rounded-[var(--surface-radius)] border" style={{ marginTop: "var(--command-top)", maxWidth: "var(--command-max-w)", borderColor: TOKENS.line, background: TOKENS.bg0, boxShadow: `0 28px 90px ${TOKENS.shadow}` }}>
                <div className="border-b p-4" style={{ borderColor: TOKENS.line }}>
                  <div className="flex items-center gap-3 rounded-full border px-4 py-3" style={{ borderColor: TOKENS.line, background: TOKENS.bg1 }}>
                    <SearchGlyph className="h-4 w-4" style={{ color: TOKENS.ink3 }} />
                    <span className="text-sm" style={{ color: TOKENS.ink3 }}>Jump to planes, views, runs, files, actions...</span>
                    <button onClick={() => setCommandOpen(false)} className="ml-auto rounded-full border px-2 py-1 text-[10px] uppercase tracking-[0.18em]" style={{ borderColor: TOKENS.line, color: TOKENS.ink3 }}>esc</button>
                  </div>
                </div>

                <div className="grid gap-4 p-4 sm:p-5 md:grid-cols-[1.1fr_0.9fr_0.9fr] md:gap-6">
                  <div className="grid gap-3">
                    <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Jump within {domain.label}</div>
                    {domain.nodes.map((item) => (
                      <button key={item} onClick={() => jumpTo(domain.id, item)} className="flex items-center justify-between rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: item === safeNode ? domain.tint : TOKENS.line, background: item === safeNode ? domain.soft : TOKENS.bg1, color: TOKENS.ink1 }}>
                        <span>{item}</span>
                        <ArrowGlyph className="h-4 w-4" style={{ color: item === safeNode ? domain.tint : TOKENS.ink3 }} />
                      </button>
                    ))}
                  </div>

                  <div className="grid gap-3">
                    <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Go to another plane</div>
                    {DOMAINS.map((item) => {
                      const Icon = item.icon;
                      return (
                        <button key={item.id} onClick={() => jumpTo(item.id)} className="flex items-center gap-3 rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: item.id === domain.id ? item.tint : TOKENS.line, background: item.id === domain.id ? item.soft : TOKENS.bg1, color: TOKENS.ink1 }}>
                          <Icon className="h-4 w-4" style={{ color: item.id === domain.id ? item.tint : TOKENS.ink3 }} />
                          <span>{item.label}</span>
                        </button>
                      );
                    })}
                  </div>

                  <div className="grid gap-3">
                    <div className="text-[10px] uppercase tracking-[0.22em]" style={{ color: TOKENS.ink3 }}>Actions</div>
                    <button onClick={() => { setSidebarOpen((value) => !value); setCommandOpen(false); }} className="rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>{sidebarOpen ? "Hide sidebar" : "Show sidebar"}</button>
                    <button onClick={() => { setInspectorOpen((value) => !value); setCommandOpen(false); }} className="rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>{inspectorOpen ? "Hide inspector" : "Show inspector"}</button>
                    <button onClick={() => jumpTo("runtime", "Runs")} className="rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>Open live runs</button>
                    <button onClick={() => jumpTo("work", "Files")} className="rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>Open files explorer</button>
                    <button onClick={() => jumpTo("finance", "Spend")} className="rounded-2xl border px-4 py-3 text-left text-sm" style={{ borderColor: TOKENS.line, background: TOKENS.bg1, color: TOKENS.ink1 }}>Inspect spend surface</button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}
