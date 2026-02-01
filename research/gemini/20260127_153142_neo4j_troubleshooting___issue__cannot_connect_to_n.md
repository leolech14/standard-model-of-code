# Research: Neo4j troubleshooting:

ISSUE: Cannot connect to Neo4j via browser at localhost:7474

What we've tri...

> **Date:** 2026-01-27 15:31:42
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:fb368d3c87a737b10a815e0693c43110d6cbc4978e658037fe8cd47474cfa2cf`
> **Raw JSON:** `raw/20260127_153142_neo4j_troubleshooting___issue__cannot_connect_to_n.json`

---

## Query

Neo4j troubleshooting:

ISSUE: Cannot connect to Neo4j via browser at localhost:7474

What we've tried:
- Installed Neo4j 2025.12.1 via Homebrew
- Service shows 'started' (brew services list)
- Port 7474 is LISTENING (verified via lsof)
- Auth files cleared (rm auth*)
- Service restarted multiple times
- Default credentials: neo4j/neo4j

ERROR IN BROWSER:
- URL: bolt://localhost:7474 → 'Could not reach Neo4j'
- URL: neo4j://localhost:7474 → Same error
- Tries to auto-retry with bolt:// scheme

LOGS SHOW:
- Started successfully
- HTTP enabled on localhost:7474
- Bolt enabled on localhost:7687
- But browser can't connect

Question: What's the correct connection URL and why isn't browser connecting?

---

## Response

Okay, this is a classic Neo4j connection confusion, and the logs you provided are the smoking gun!

As a senior software engineer, I've seen this exact pattern many times. Let's break it down:

### The Core Issue: Protocol Mismatch

You are attempting to connect to the Neo4j Browser using the `bolt://` or `neo4j://` protocol on port `7474`. However, your Neo4j instance is configured to serve **HTTP** on `7474` and the **Bolt** protocol on `7687`.

Your browser is correctly reporting "Could not reach Neo4j" because it's speaking "Bolt" to a port that expects "HTTP".

### Correct Connection URLs

1.  **To access the Neo4j Browser (the web interface itself):**
    Use `http://localhost:7474`

2.  **Once *inside* the Neo4j Browser, to connect to the database instance:**
    You will be prompted for the database URI. Here, you should use `bolt://localhost:7687`.
    *(The default credentials `neo4j`/`neo4j` should work if you cleared the auth files.)*

### Why your browser isn't connecting with `bolt://localhost:7474`

Your own logs provide the definitive answer:

*   **`HTTP enabled on localhost:7474`**: This clearly states that port `7474` is for the **HTTP protocol**, which serves the Neo4j Browser's static web assets and initial connection.
*   **`Bolt enabled on localhost:7687`**: This clearly states that the **Bolt protocol** (the native binary protocol for client-server communication with Neo4j) is listening on port `7687`.

When you try `bolt://localhost:7474`, your browser attempts to initiate a Bolt handshake on a port that expects an HTTP request. It's like calling a landline phone and trying to speak to a radio. They're both communication, but different protocols.

The Neo4j Browser (the web application) is *served* over HTTP. Once it's loaded in your browser, it then makes an *internal* connection to the Neo4j database using the Bolt protocol.

### Summary & Action Plan

1.  Open your web browser.
2.  Navigate to `http://localhost:7474`. This will load the Neo4j Browser application.
3.  Once the browser application loads, it will typically prompt you for a connection URI. Enter `bolt://localhost:7687`.
4.  Enter the default username `neo4j` and password `neo4j`.
5.  You should now be connected to your Neo4j database.

This should resolve your connection issue. Good job on collecting those detailed logs! They were absolutely critical for diagnosing this.

---

## Citations

_No citations provided_
