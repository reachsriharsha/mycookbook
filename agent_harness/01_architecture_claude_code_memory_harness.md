# Claude Code Development Harness: Architecture Deep Dive

## The Core Problem: Zero-State Conversations

Every conversation with Claude Code starts from zero. There is no memory between sessions — no recall of past decisions, project context, or conversation history. As sessions accumulate (700+ in weeks), developers lose track of what was done, what was decided, and where things left off. Worse, mid-session context compaction at ~60% token usage silently drops critical decisions.

```
 SESSION 1          SESSION 2          SESSION 3          SESSION N
┌───────────┐    ┌───────────┐    ┌───────────┐       ┌───────────┐
│ Decisions │    │ Decisions │    │ Decisions │  ...  │ Decisions │
│ Context   │    │ Context   │    │ Context   │       │ Context   │
│ Files     │    │ Files     │    │ Files     │       │ Files     │
└─────┬─────┘    └─────┬─────┘    └─────┬─────┘       └─────┬─────┘
      │                │                │                     │
      ▼                ▼                ▼                     ▼
   🗑️ LOST          🗑️ LOST          🗑️ LOST              🗑️ LOST

         ══════════════════════════════════════════
              No persistent memory between any sessions
         ══════════════════════════════════════════
```

**The default search approach (grep) is also broken:**
Claude Code's built-in search sends a Haiku sub-agent to grep through every file — it's slow (~3 minutes), token-expensive, and matches strings not meaning (e.g., searching "sleep" returns `sleep()` function calls alongside actual sleep notes).

---

## The Solution: A Three-Layer Memory Harness

The architecture replaces grep with a local semantic search engine (QMD), wraps it in a Claude Code skill (`/recall`), and auto-indexes sessions via hooks — creating persistent, searchable memory across all conversations.

```mermaid
graph TB
    subgraph "Layer 3: Interface — Claude Code Skills"
        R["/recall Skill"]
        S["/sync-claude-sessions"]
        R --> |temporal| TEMP["Temporal: yesterday, last week"]
        R --> |topic| TOP["Topic: BM25 across collections"]
        R --> |graph| GRH["Graph: Interactive visualization"]
    end

    subgraph "Layer 2: Search Engine — QMD"
        BM["BM25 — Keyword Search<br/>Deterministic, fast, ranked by TF-IDF"]
        SEM["Semantic — Vector Search<br/>Embeddings, meaning-based"]
        HYB["Hybrid — Combined<br/>BM25 + Semantic + LLM reranking"]
    end

    subgraph "Layer 1: Knowledge Base — Obsidian Vault"
        N["📝 Notes"]
        D["📅 Daily Entries"]
        SE["💬 Sessions (JSONL → MD)"]
        T["🎙️ Transcripts"]
        SK["⚙️ Skills / Recipes"]
    end

    R --> BM
    R --> SEM
    R --> HYB
    BM --> N & D & SE & T & SK
    SEM --> N & D & SE & T & SK
    HYB --> N & D & SE & T & SK
    S --> |"hook: on session close"| SE

    style R fill:#6C5CE7,color:#fff
    style S fill:#6C5CE7,color:#fff
    style BM fill:#00B894,color:#fff
    style SEM fill:#00B894,color:#fff
    style HYB fill:#00B894,color:#fff
```

---

## Layer 1: The Knowledge Base (Obsidian Vault)

The foundation is an Obsidian vault organized into QMD collections — each folder maps one-to-one to a searchable collection.

```
obsidian-vault/
├── notes/                    ← QMD Collection: "notes"
│   ├── project-alpha.md
│   ├── architecture-decisions.md
│   └── research/
│       └── graph-approaches.md
├── daily/                    ← QMD Collection: "daily"
│   ├── 2026-03-01.md
│   ├── 2026-03-02.md
│   └── 2026-03-03.md
├── sessions/                 ← QMD Collection: "sessions"
│   ├── session-2026-03-01-09-15.md
│   ├── session-2026-03-01-14-30.md
│   └── session-2026-03-02-08-00.md
├── transcripts/              ← QMD Collection: "transcripts"
│   └── meeting-standup-mar3.md
└── skills/                   ← QMD Collection: "skills"
    ├── recall/
    │   └── SKILL.md
    └── sync-sessions/
        └── SKILL.md
```

### Session Indexing Pipeline

Claude Code stores all conversations as JSONL files on your local machine. The raw files contain tool uses, system prompts, roles — everything. The pipeline parses out the signal (actual user messages, decisions, outcomes) and converts it to clean markdown, which QMD then indexes.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │     │   Parser/Hook    │     │  Obsidian Vault │
│  JSONL Sessions │────▶│  (on close)      │────▶│  sessions/*.md  │
│  ~/.claude/     │     │  Extract signal   │     │                 │
│  sessions/      │     │  Strip noise      │     │  Clean markdown │
└─────────────────┘     └──────────────────┘     └───────┬─────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │  QMD Index  │
                                                  │  (embed)    │
                                                  │  BM25 + Vec │
                                                  └─────────────┘
```

---

## Layer 2: The Search Engine (QMD)

QMD is a local CLI search engine by Tobias Lutke (CEO, Shopify). It runs entirely on your machine — no cloud, no API calls. It supports three search modes that solve different problems:

### Search Mode Comparison

```
┌──────────────────────────────────────────────────────────────────────┐
│                     SEARCH MODE COMPARISON                          │
├─────────────┬────────────────────┬───────────────────────────────────┤
│  Mode       │  Command           │  How it works                    │
├─────────────┼────────────────────┼───────────────────────────────────┤
│  BM25       │  qmd search        │  Exact keyword match + ranking   │
│  (Default)  │  "query" -c notes  │  by term frequency & rarity.     │
│             │                    │  No AI. Pure math. Instant.      │
├─────────────┼────────────────────┼───────────────────────────────────┤
│  Semantic   │  qmd vsearch       │  Embedding-based. Finds meaning  │
│             │  "query" -c notes  │  even when exact words don't     │
│             │                    │  appear. Needs `qmd embed` run.  │
├─────────────┼────────────────────┼───────────────────────────────────┤
│  Hybrid     │  qmd query         │  BM25 + Semantic + LLM rerank.   │
│             │  "query"           │  Best results, slightly slower.  │
│             │                    │  The gold standard.              │
└─────────────┴────────────────────┴───────────────────────────────────┘
```

### Grep vs BM25 vs Semantic — Concrete Example

Searching for "sleep" across a vault:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  GREP                          │ 200 files. Noise everywhere.          │
│  (string matching)             │ Finds: sleep(), "sleep mode",         │
│                                │ code comments, CSS classes...         │
│  ❌ No ranking. No relevance.  │ 3 minutes with Haiku sub-agent.      │
├────────────────────────────────┼───────────────────────────────────────┤
│  BM25                          │ Focused results in 2 seconds.        │
│  (keyword + ranking)           │ Ranks by frequency + rarity.         │
│                                │ A short note mentioning "sleep"      │
│  ✅ Relevance-ranked.          │ 5x scores higher than a 10K-word     │
│     No AI needed.              │ file where it appears once.          │
├────────────────────────────────┼───────────────────────────────────────┤
│  SEMANTIC                      │ Search "couldn't sleep, bad night"   │
│  (meaning-based)               │ → Finds "bedtime discipline goal"    │
│                                │ even though those exact words         │
│  ✅ Finds meaning.             │ don't appear. 4/5 results have NO    │
│     Beyond keywords.           │ matching keywords at all.            │
├────────────────────────────────┼───────────────────────────────────────┤
│  HYBRID                        │ Combines both. "couldn't sleep,      │
│  (BM25 + Semantic + rerank)    │ bad night" → returns results         │
│                                │ ranked at 89%, 51%, 42%.             │
│  ✅ Best of both worlds.       │ Best ranking of all approaches.      │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## Layer 3: The Skill Interface (/recall)

`/recall` is a Claude Code skill that sits on top of QMD. It loads context *before* you start working — instead of explaining what you were doing, you tell it to recall.

### Three Recall Modes

```mermaid
graph LR
    RECALL["/recall"] --> T["⏰ Temporal"]
    RECALL --> TO["📚 Topic"]
    RECALL --> G["🕸️ Graph"]

    T --> T1["/recall yesterday"]
    T --> T2["/recall last week"]
    TO --> TO1["/recall topic graph"]
    TO --> TO2["/recall topic auth system"]
    G --> G1["/recall graph last week"]

    T1 --> |"Scans session history"| OUT1["39 sessions reconstructed<br/>Timeline + message counts<br/>+ what was done when"]
    TO1 --> |"BM25 across collections"| OUT2["Dashboard, production plan,<br/>to-do list — all related files<br/>in < 1 minute"]
    G1 --> |"Interactive HTML"| OUT3["Sessions as colored blobs<br/>Files clustered by type<br/>Connections = file touches"]

    style RECALL fill:#6C5CE7,color:#fff
    style T fill:#FDCB6E,color:#000
    style TO fill:#74B9FF,color:#000
    style G fill:#FF7675,color:#fff
```

**Temporal** — Reconstructs session history by date. Shows timeline, message count per session, and what was done. Example: `/recall yesterday` rebuilds 39 sessions from one day.

**Topic** — BM25 search across all QMD collections in parallel. Example: `/recall topic QMD video` returns dashboard, production plan, and to-do list — all related files surfaced in under a minute.

**Graph** — Opens an interactive HTML visualization. Sessions appear as colored blobs (older ones dimmer, recent ones brighter). Files are clustered by type: goals, research, voice, docs, content, skills. Hover to highlight connections, click to select and copy file paths into Claude Code.

---

## The Automation Loop: Hooks & Sync

The magic is that the index stays fresh without manual work. A Claude Code hook fires at the end of every session, exporting and embedding the conversation into QMD automatically.

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTOMATIC SESSION PIPELINE                     │
│                                                                  │
│   You work in        Session closes     Hook fires              │
│   Claude Code   ───▶ (terminal close) ───▶ /sync-claude-sessions│
│                                             │                    │
│                                             ▼                    │
│                                      Parse JSONL                 │
│                                      Extract signal              │
│                                      Write to vault/sessions/    │
│                                             │                    │
│                                             ▼                    │
│                                      qmd embed                   │
│                                      (re-index)                  │
│                                             │                    │
│                                             ▼                    │
│                                      Index is fresh ✅           │
│                                      Next session can /recall    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cross-Device Sync Architecture

The memory layer is tool-agnostic. It works across Claude Code, OpenClaw, Gemini CLI, or any future tool — because your context lives in your vault, not in any single application.

```
┌──────────────────────────────────────────────────────────────┐
│                    YOUR CONTEXT (PORTABLE)                     │
│                                                               │
│   ┌──────────┐    Obsidian Sync    ┌──────────────────┐      │
│   │  MacBook  │◄──────────────────▶│   Mac Mini        │      │
│   │           │                    │   (always on)     │      │
│   │ Claude    │                    │   OpenClaw 24/7   │      │
│   │ Code      │                    │   QMD index       │      │
│   └──────────┘                    └──────────────────┘      │
│        │                                   ▲                  │
│        │          Same vault               │                  │
│        │          Same QMD index           │                  │
│        │          Same skills              │                  │
│        ▼                                   │                  │
│   ┌──────────┐                             │                  │
│   │  Phone   │─────── Obsidian Sync ───────┘                  │
│   │ OpenClaw │                                                │
│   └──────────┘                                                │
│                                                               │
│   Tools change. Models change. Your context stays.            │
└──────────────────────────────────────────────────────────────┘
```

---

## End-to-End Data Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant CC as Claude Code
    participant Hook as Session Hook
    participant Vault as Obsidian Vault
    participant QMD as QMD Engine
    participant Recall as /recall Skill

    Note over Dev,Recall: SESSION N: Starting work
    Dev->>Recall: /recall topic "auth system"
    Recall->>QMD: qmd search "auth system" -c sessions -n 5
    Recall->>QMD: qmd search "auth system" -c notes -n 5
    QMD->>Vault: Search BM25 index
    Vault-->>QMD: Ranked results
    QMD-->>Recall: Top matches with snippets
    Recall-->>CC: Context loaded (past decisions, file paths, notes)
    CC-->>Dev: "Based on your previous sessions, here's where we left off..."

    Note over Dev,Recall: Working... (full context loaded)
    Dev->>CC: Continue working on auth system
    CC->>CC: Work with full project context

    Note over Dev,Recall: Session ends
    CC->>Hook: Terminal closes → hook fires
    Hook->>Hook: Parse JSONL → extract signal
    Hook->>Vault: Write sessions/session-YYYY-MM-DD.md
    Hook->>QMD: qmd embed (re-index)
    QMD-->>QMD: Update BM25 + vector indexes

    Note over Dev,Recall: SESSION N+1: Next day
    Dev->>Recall: /recall yesterday
    Recall->>QMD: Temporal scan
    QMD-->>Recall: 39 sessions, timeline, summaries
    Recall-->>Dev: Full reconstruction of yesterday's work
```

---

## Key Design Principles

**1. Local-first** — All data, embeddings, and indexes live on your machine. No cloud dependency, no API costs for search.

**2. Tool-agnostic** — The memory layer (vault + QMD) works across any AI tool. When models or tools change, your context remains.

**3. Automatic indexing** — Session hooks ensure the index is always fresh without manual export steps.

**4. Relevance over recall** — BM25 and semantic search replace grep's brute-force string matching with ranked, meaningful results.

**5. Skill-based interface** — Claude Code natively understands skills, so `/recall` works without any special configuration — just drop it in `.claude/skills/`.

---

*Based on "Grep Is Dead: How I Made Claude Code Actually Remember Things" by Artem Zhutov (@ArtemXTech), March 2026.*
