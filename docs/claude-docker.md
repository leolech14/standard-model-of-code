
You said:

Explain

https://www.docker.com/blog/run-claude-code-locally-docker-model-runner/
ChatGPT said:

Thought for 6s
That post is basically a “wiring guide” that lets Claude Code (Anthropic’s CLI coding agent) talk to a local model running through Docker Model Runner (DMR) instead of calling Anthropic’s hosted API. The goal: keep your code/data local, control costs, and still use the Claude Code workflow.

The core idea
Claude Code is a terminal tool that reads your repo, explains code, runs routine tasks, and can help with git workflows via natural language.

Docker Model Runner can run LLMs locally and exposes an Anthropic-compatible API, so Claude Code can point at it without needing a custom integration.

The bridge is one environment variable: ANTHROPIC_BASE_URL (Claude Code supports custom endpoints through it).

What you actually do (high level)
1) Install Claude Code
Docker’s post links to the official install commands for macOS/Linux and Windows.

2) Make sure DMR is reachable locally
If you’re using Docker Desktop, you enable TCP access for the model runner, and then it’s reachable at http://localhost:12434.

docker desktop enable model-runner --tcp
3) Point Claude Code at DMR and pick a local model
You run Claude Code with:

ANTHROPIC_BASE_URL=http://localhost:12434 claude --model <model-name> "Describe this repo."
…and now Claude Code sends requests to your local DMR instance.

The “context size” section matters a lot for coding
The post highlights that for repo-scale coding, context length is often the limiter:

Some models (examples given: glm-4.7-flash, qwen3-coder, devstral-small-2) ship with 128K context by default.

gpt-oss defaults to 4,096 tokens, but DMR can repackage a model with a larger context window.

Example they show: pull gpt-oss, package a 32k variant, then use it from Claude Code.

docker model pull gpt-oss
docker model package --from ai/gpt-oss --context-size 32000 gpt-oss:32k
ANTHROPIC_BASE_URL=http://localhost:12434 claude --model gpt-oss:32k "Describe this repo."
Observability / debugging: see exactly what Claude Code is sending
They show a neat trick: DMR can display the raw requests coming from Claude Code, which is useful for debugging “why did the agent do that?” or checking compatibility.

docker model requests --model gpt-oss:32k | jq .

Make it persistent (quality-of-life)
Instead of repeating the env var each time, you can export it in your shell profile (bash/zsh/etc.), then run claude ... normally while still using the local endpoint.

If you tell me your setup (Docker Desktop vs Engine on Linux, and which model you want to run), I can translate this into a “do-this-first, verify-that-next” checklist tailored to your machine and goals.

You said:
Okay, but what, how will I run such big models on my local machine?
ChatGPT said:

Thought for 13s
You usually don’t run the “big-big” models locally in full precision. You run smaller models, or big models in quantized form, and you accept some tradeoffs (speed/quality/context).

Here’s the practical reality checklist.

1) “Big model” = RAM/VRAM problem first
A rough mental model:

FP16 (half precision): ~2 bytes per parameter

7B ≈ 14 GB

13B ≈ 26 GB

70B ≈ 140 GB

Quantized (common for local):

Q4 ≈ ~0.5 bytes/param → 70B ≈ ~35 GB (plus overhead)

Q5/Q6/Q8 scale up from there

So if your machine has 16–32 GB unified memory, a 70B model is not realistically comfortable unless you do aggressive quantization and accept it being slow and tight on memory.

2) Then there’s the “context window tax” (KV cache)
Even if the weights fit, long context (32k/128k) can blow up memory usage because the model has to keep a big attention cache (KV cache). So the trick is:

Run smaller context for local dev (e.g., 8k–16k)

Use RAG / file indexing instead of stuffing the whole repo into the prompt

Only go huge-context when you have a machine that can afford it

3) What you can realistically run on common local setups
Apple Silicon laptops (unified memory)
Good news: Apple Silicon runs LLMs decently because RAM is shared and Metal acceleration exists.

16 GB: sweet spot is 3B–8B models (Q4/Q5), maybe 13B Q4 with compromises

32 GB: 7B–14B very comfortably; 20–34B Q4 sometimes workable depending on context

64 GB: you start flirting with 70B Q4 (still not “fast”, but feasible)

If you’re thinking “MacBook Pro M4 Pro”-class: those are great for 7B–32B local work, and “big” models become a “sometimes” thing depending on memory.

NVIDIA GPU desktops (VRAM)
This is the other “local big model” path:

12 GB VRAM: 7B–13B fast, some 20B-ish quantized

24 GB VRAM (4090): 34B comfortably; 70B Q4 can be made to run with offload tricks, but context still matters

48+ GB VRAM: genuinely comfortable with big models and larger contexts

CPU-only is possible, but for big models it becomes “go make coffee” slow.

4) So… how do people do it in practice?
They usually choose one of these strategies:

A) “Small-but-sharp” local models (most common)
Run a good 7B–14B coder model locally for 80% of tasks:

quick refactors

code search + explanation

unit test writing

glue code

small feature implementation

Then occasionally use cloud for:

huge refactors

deep reasoning across many files

very long context sessions

B) Quantize aggressively
If you must run bigger:

use Q4/Q5 (most common balance)

keep context sane (8k–16k)

accept slower tokens/sec

C) Use MoE models
Mixture-of-Experts models can “feel big” while only activating a portion of parameters per token. They can be more feasible locally than their headline size suggests (still heavy, but sometimes a better deal).

D) Don’t brute-force context—index the repo
Instead of pushing your whole repo into the model:

use repo indexing (ripgrep + embeddings + retrieval)

only feed the relevant chunks
This is exactly how you keep local models useful on real codebases.

5) What this means for the Docker Model Runner + Claude Code setup
That Docker setup works great if the model you choose matches your hardware reality:

Pick a model size your machine can run comfortably (usually 7B–14B)

Don’t chase 128k context locally unless you have the memory headroom

Use retrieval / “context refinery” style pipelines for repo-scale understanding

If you tell me your machine specs (Apple Silicon + unified memory size or NVIDIA GPU + VRAM), I’ll give you a concrete menu like:

“Best local coder model for your hardware”

“Max size you can run without pain”

“Recommended quantization + context settings”

“Expected speed tier (fast/ok/slow)”

No fluff—just the viable options.

You said:
All right, so when it says that I can run Cloud Code on my, locally on my computer using Docker, is it referring to the big models like Opus 4.5?
ChatGPT said:

Thought for 8s
No — that Docker “run Claude Code locally” setup is not running Anthropic’s Opus 4.5 (or Sonnet 4.5) on your machine. It’s running other models you have locally (typically open-source or locally-packaged models), and Claude Code is just talking to them through an Anthropic-compatible endpoint.

What “run Claude Code locally” actually means
Claude Code is the client (the agent/CLI). Docker Model Runner is the local inference server. The blog’s trick is:

Docker Model Runner exposes an Anthropic-compatible API

Claude Code can be pointed at a custom endpoint via ANTHROPIC_BASE_URL

So Claude Code sends “Anthropic-style” requests to http://localhost:12434 instead of Anthropic’s cloud

That’s why the blog examples mention models like glm-4.7-flash, qwen3-coder, devstral-small-2, gpt-oss — those are the models you’d be running locally via Docker, not Opus/Sonnet.

Where Opus 4.5 fits
In Claude Code docs, opus is an alias that maps to Opus 4.5 — but that refers to using Anthropic’s hosted model (unless you override the endpoint).

So you have two modes:

Cloud mode (Anthropic-hosted): claude --model opus → uses Opus 4.5 remotely

Local mode (Docker Model Runner): ANTHROPIC_BASE_URL=http://localhost:12434 ... → uses whatever local model name you specify (like qwen3-coder, gpt-oss:32k, etc.)

The punchline
If you point Claude Code at Docker Model Runner, you are not “running Opus 4.5 locally” — you’re running a different local model behind a compatible API.

If you tell me your machine (Mac + how much unified memory, or PC + GPU/VRAM), I’ll suggest a realistic “local Opus substitute” model tier (fast vs strong) and the context window settings that won’t melt your RAM.

You said:
Oh, okay, so it would be using open source models inside of the Cloud Code CLI scaffold and all the intrinsic logic of data management and the API calls and the sub-agents, and it is using the complete, full, updated, like, latest version of Cloud Code CLI.
ChatGPT said:
Yep — that’s the right mental model, with one important caveat.

What stays the same (the “Claude Code scaffold”)
When you point Claude Code at Docker Model Runner, you’re still using:

the actual Claude Code CLI (same workflows, same repo-scanning behavior, same tool orchestration style)

the same prompt packaging / request format (Anthropic-style API calls)

the same local file ops Claude Code does (reading/writing files, running commands, diffing, etc.), because that’s the CLI’s job, not the model’s

So yes: you’re essentially swapping the brain (model) while keeping the body (Claude Code agent runtime).

The caveat: model capability changes what “intrinsic logic” can really do
Claude Code can try to use the same patterns (planning, iterative edits, tool use), but some things depend on whether the model behind Docker Model Runner:

follows tool-use / structured output reliably

handles long context well

is strong at code navigation and refactoring

stays consistent over multi-step tasks

So the CLI is “the same”, but how well sub-agent-like behavior and multi-step workflows work depends heavily on the local model.

About “complete, full, updated, latest”
You’re using the “latest” Claude Code only if you installed/updated it to the latest on your machine. Docker Model Runner doesn’t magically upgrade Claude Code — it just provides the local endpoint.

A quick way to sanity-check in practice is:

check Claude Code version (whatever command it provides in your install)

run one small task in cloud mode, then the same task with ANTHROPIC_BASE_URL=... and compare behavior

One more practical implication
This setup often ends up being a two-tier workflow:

local open-source coder model for fast iterations + privacy

cloud Opus/Sonnet for the “hard parts” (big refactors, deep reasoning, huge-context tasks)

If you tell me your exact machine (Mac model + unified memory, or PC GPU + VRAM), I’ll recommend a realistic local model size + quantization level that makes Claude Code feel “native” instead of “wobbly.”

You said:
Okay, what about long context models via open source? And what about speeding things up? I know that some maybe open router, or maybe Oluma, or maybe another way of accessing open source models, I could access for free and with the speed of, I don't know, maybe 30 tokens per second. But if I used credits, it would speed things up to 300, 400 tokens per second. So how is that, how can we use this approach then of accessing cloud code via this Docker setup and have this list of models that we can even pay, we can pay for compute to make them even higher context windows and higher speed.
ChatGPT said:

Thought for 1m 35s
Yes — you can absolutely do “long-context + paid-for-speed” with the same Claude Code workflow. The trick is: Claude Code only cares that it’s talking to an Anthropic Messages API (/v1/messages). Where that endpoint lives (local Docker, a gateway, OpenRouter, a dedicated fast inference provider) is up to you.

Below are the workable patterns.

1) Long-context open(-weight) models you can use
Some strong long-context options right now:

Qwen2.5-Coder: up to 128K context (good “daily driver” coder).

DeepSeek-Coder-V2: 128K context.

Llama 3.1 (8B/70B/405B): 128K context.

Qwen3-Coder (MoE): 256K native, and they claim it can be extended up to 1M with YaRN techniques (provider-dependent).

Reality check: long context is expensive (KV cache). Even if a model “supports 128K/256K”, you won’t want to run that max context locally unless you have a lot of memory and you accept slower inference.

2) Speed: why “free 30 t/s” vs “paid 300+ t/s” happens
Throughput is mostly about hardware + inference stack optimizations:

Some providers advertise hundreds of tokens/sec on certain models (e.g., Groq ~300 t/s in their own materials/benchmarks; Together shows peaks >300 t/s for specific deployments).

Others are slower but cheaper, or fluctuate (shared serverless).

So “paying credits” typically buys you:

faster chips / better kernels

less contention

better batching / speculative decoding

sometimes “turbo” endpoints

3) How to keep Claude Code + Docker-style setup, but choose cloud models and pay for speed
Option A — Easiest: OpenRouter “Anthropic Skin” (no extra proxy)
OpenRouter explicitly supports Claude Code by letting you set:

ANTHROPIC_BASE_URL=https://openrouter.ai/api
…and Claude Code will talk to OpenRouter using its native protocol.

OpenRouter also supports provider routing preferences, including selecting for minimum throughput (tokens/sec).

So you can:

run Qwen3-Coder 256K for repo-scale tasks when needed

run a fast small model for quick edits

pay to pick faster providers / higher throughput

Option B — “One endpoint to rule them all”: run a gateway (LiteLLM) in Docker
Anthropic’s own Claude Code docs basically recommend the “LLM gateway” pattern: a single proxy layer for auth, routing, fallbacks, cost controls.

LiteLLM can expose the Anthropic /v1/messages format while routing to many backends.

That means you can point Claude Code at:

local Docker Model Runner for “free-ish” local inference

OpenRouter for broad model access + routing

a speed-focused provider for “turbo” throughput (where available)

…all without changing Claude Code, just by changing the gateway config.

Claude Code supports this explicitly via env vars like:

ANTHROPIC_BASE_URL=...

ANTHROPIC_AUTH_TOKEN=...

4) How you’d actually use this day-to-day (the winning workflow)
You set up 2–3 model “tiers” behind the endpoint you point Claude Code at:

Fast/cheap (small-ish coder, short context)

for interactive iteration, tests, quick refactors

Long-context (128K/256K)

for “read lots of files / repo-scale reasoning”, big diffs, architectural analysis

Premium reasoning (if you want to keep Claude cloud models too)

for the hardest steps

Then in Claude Code you either:

choose with claude --model <name> (where <name> maps to whatever your endpoint supports), or

let the gateway route based on rules (latency/throughput/cost).

5) Where Ollama fits in this picture
Ollama is great locally, but by default it speaks OpenAI-ish endpoints — while Claude Code expects Anthropic Messages (/v1/messages). That’s why you either:

use Docker Model Runner (it already offers Anthropic compatibility),

or put a proxy/gateway in between.

If you tell me your hardware (Mac + unified memory, or PC + GPU/VRAM) and whether you prefer OpenRouter direct or a gateway in Docker, I’ll give you a concrete “starter pack” model lineup (fast / long-context / heavy) + the exact env vars to make Claude Code switch between them smoothly.

You said:
Okay, and what are the aspects that make cloud code CLI feel like cloud code CLI when you interact with it? Is it more from the models or is it more from the CLI tool scaffold?
ChatGPT said:
It’s both, but in different ways.

Think of “Claude Code CLI feel” as the agent runtime + the model’s competence interacting. The CLI gives you the workflow and tooling. The model determines whether that workflow feels smooth, smart, and trustworthy.

What comes from the CLI scaffold (you keep this even with open-source models)
These are the “this is definitely Claude Code” vibes:

Repo-aware workflow: it knows it’s operating inside a codebase, and it frames answers around files, diffs, and next steps.

Tool orchestration: reading files, editing files, running commands/tests, checking outputs, iterating.

Patch/diff-style edits: making targeted changes instead of dumping whole files.

Multi-step “agent loop”: plan → act → verify → adjust (even if it doesn’t always say it explicitly).

Session conventions: how it summarizes what changed, where, and why; the conversational rhythm; the guardrails around destructive actions.

Local data handling: how it gathers context (what it reads, when it asks for more), and how it avoids slamming the whole repo into one prompt.

If you swap the model but keep Claude Code, you still get this structure.

What comes from the model (this is what most people interpret as “feel”)
This is the part that makes it feel premium vs wobbly:

Planning quality: does it pick the right strategy, or thrash?

Navigation intuition: does it jump to the right files quickly?

Edit precision: small changes that compile vs big messy rewrites.

Tool-use reliability: does it follow the protocol (structured outputs, calling tools when needed), or does it hallucinate actions?

Error recovery: when a test fails, does it diagnose correctly and converge fast?

Consistency over many turns: does it remember what it decided and stay coherent?

Long-context discipline: can it use large context without losing the thread?

This is why a great 7B can feel “okay” but not “Claude,” while a strong model makes the exact same CLI suddenly feel like a senior engineer.

The split in one sentence
The CLI creates the agent experience (repo ops + iterative workflow).

The model creates the intelligence that makes that experience satisfying.

What changes when you point Claude Code at local/open models
You’ll still feel:

the same scaffolding (commands, diffs, file edits, tests)

But you may lose (depending on model):

the “it just knows where to look”

the “it converges in 1–2 iterations”

the “it never breaks the codebase with a sweeping rewrite”

If you want the closest “real Claude Code” feel with non-Anthropic models
Prioritize models/providers that are strong at:

coding + refactoring

tool-use / instruction-following

long context without derailing

And keep the workflow smart:

use retrieval/indexing instead of maxing context

run tests automatically

constrain edits to small diffs

If you tell me what you care about most—speed, long context, or highest-quality reasoning—I’ll suggest a 2–3 model setup that keeps the Claude Code “feel” while still letting you route to cheaper/faster long-context compute when you want.

You said:
Let's make an updated list of the models, okay? Search on Hugging Face. Today is the 30th of January of 2026. Let's check what we have and let's rank for speed. And I don't mean only the models, but the platforms that let me access the models and pay for it that can speed things up. You must include this on the list. Not only speed, but context window and the benchmarks for coding and tool using and this other instruction following, all these aspects, okay, that you have already mentioned.
ChatGPT said:

Thought for 1m 17s
Yep — we can build a current (Jan 30, 2026) “menu” that covers open(-weight) coding models on Hugging Face, plus the platforms that can serve them fast (and sometimes with bigger context if you pay for higher tiers / better hardware).

I’ll split this into two parts:

Models (what brain you’re using)

Platforms (how fast / how long-context you can run that brain)

And I’ll anchor the “quality” side to widely used benchmarks:

SWE-bench Verified for real repo bug-fixing (agent-like coding).

LiveCodeBench for contamination-resistant coding problems over time.

BigCodeBench for harder programming tasks.

BFCL (Berkeley Function Calling Leaderboard) for tool/function calling accuracy (instruction-following + tool use).

1) Updated Hugging Face shortlist: long-context + coding + agent/tool-use vibe
Tier A: “Repo-scale / agentic coding” (huge context, built for tool use)
Qwen3-Coder-480B-A35B-Instruct (MoE)

Context: 256K native, “extendable to 1M” with YaRN (implementation/provider dependent).

Why it’s on the list: explicitly positioned for agentic coding + a designed function-call format.

Local reality: not a casual local run. It’s a “cloud served” model for most people.

Qwen3-Next-80B-A3B-Instruct

Context: shows 256K configuration examples with vLLM.

Why it’s interesting: often a better “big but feasible” option than 480B MoE, depending on provider.

Tier B: “Long-context coders you can actually deploy”
Qwen2.5-Coder-32B-Instruct

Context: 131,072 tokens on the model card.

Why it’s a workhorse: very strong coding for its size; long context without being monstrous.

DeepSeek-Coder-V2

Known for strong coding claims vs closed models in its release materials.

(Context is commonly referenced as 128K in external analyses; you’ll want to verify the exact variant you pick because DeepSeek has multiple related releases.)

Tier C: “Still good, smaller context / lighter”
StarCoder2-15B

Context: 16,384 (with sliding window details).

Why it’s here: a practical mid-size model, easy to host; great when you rely on retrieval rather than raw context.

DeepSeek-R1

Not “a coder model” first, but it’s openly released and often used as a reasoning-heavy engine that can help with code planning/verification.

2) Speed ranking: platforms that can serve these models fast (and you can pay to go faster)
Important nuance: “tokens/sec” varies by model, batch, latency mode, and whether the provider reports per-user streaming TPS vs aggregate throughput. So I’m giving you a practical ranking based on published numbers + common real-world positioning.

S-Tier speed (crazy fast)
Cerebras Inference

Published: ~2,100 tokens/sec on Llama 3.1/3.2 70B class in Cerebras materials.

Their docs show free vs paid context tiers (example page shows free ~65k and paid 128k for Llama 3.3 70B).

If your goal is “make open models feel instant,” Cerebras is one of the most extreme speed options.

A-Tier speed (very fast, commonly 200–400+ t/s on the right setups)
GroqCloud

Groq cites independent benchmarking by Artificial Analysis for very high throughput on Llama 3 family (e.g., 284 t/s for Llama 3 70B and 877 t/s for Llama 3 8B in one benchmark mention; newer posts cite other models too).

In practice: you pick from whatever models Groq hosts (not “any Hugging Face model”), but when they host it, it’s fast.

Together AI

Together markets very high throughput, and also offers serverless pay-per-token and dedicated GPU endpoints when you want consistent performance.

They also publish posts about “turbo” / optimized inference stacks and peak TPS claims.

B-Tier speed (solid, often ~100–200 t/s for interactive use; higher with premium/dedicated)
Fireworks AI

Fireworks publishes real-world throughput examples like ~145 tokens/sec for Llama 4 Maverick in one post, and up to ~130 t/s for certain DeepSeek offerings (depending on tier).

C-Tier (flexible + “deploy anything from HF”, but speed depends on instance you pay for)
Hugging Face Inference Endpoints

The value proposition is: “deploy any Hub model on dedicated autoscaling infra.”

Speed depends on what you choose (A10/L4/A100/H100/H200/B200 etc.), quantization, and server stack (TGI/vLLM/etc.). HF has its own guidance on inference optimization and benchmarking concepts.

3) “I want one list where I can also pay for speed and context” (the routing layer)
This is where aggregators/gateways matter, because they let you keep one Claude Code setup while swapping providers based on speed/context/cost.

OpenRouter (multi-provider marketplace + routing by throughput)
You can route by preferred minimum throughput (tokens/sec) and other constraints.

This is the cleanest way to say: “Use the fastest provider that can handle my context window, and if I’m paying credits, go even faster.”

Artificial Analysis leaderboard (for picking the fastest provider per model)
Artificial Analysis tracks speed/price/quality across many API endpoints and is also integrated as a Hugging Face Space/leaderboard.

This is the most practical “where do I get 300+ t/s for this model?” lookup tool.

4) How you’d use this with the Docker/Claude Code approach
You have three viable “architectures”:

Local-only (Docker Model Runner)

Great for privacy + cost, but speed/context are limited by your hardware.

Direct-to-router (OpenRouter as your Anthropic-style endpoint)

Claude Code points at OpenRouter; you choose models and enforce throughput rules.

Gateway in the middle (best “pro” setup)

Claude Code → your gateway endpoint → routes to (Cerebras/Groq/Together/Fireworks/HF Endpoints/local) depending on rules.

This is the “one endpoint, many backends” model Anthropic calls out for Claude Code gateway setups.

A practical ranked starter list (what I’d actually pick)
If you want Claude Code to feel snappy, I’d run a 3-model lineup:

Fast interactive coding (speed-first): a hosted Llama/Qwen-class model on Groq or Cerebras (depending on availability + your context needs).

Long-context repo reasoning: Qwen2.5-Coder-32B-Instruct (131K) or Qwen3-Coder (if you really need 256K+).

Tool calling reliability check: use BFCL to sanity-check whatever model you’re considering for “agent tool use.”

If you tell me:

your machine (Mac + unified memory OR GPU + VRAM), and

whether you prefer OpenRouter routing or a self-hosted gateway,

…I’ll turn this into an exact “model list + provider list + recommended context caps” specifically for your workflow (including a “fast tier” and a “deep tier” you can switch between without changing how you use Claude Code).
