Build Your Open Brain
Complete Setup Guide
The infrastructure layer for your thinking. One database, one AI gateway, one chat channel. Any AI you use can plug in. No middleware, no SaaS chains, no Zapier.

This isn't a notes app. It's a database with vector search and an open protocol — built so that every AI tool you use shares the same persistent memory of you. Claude, ChatGPT, Cursor, Claude Code, whatever ships next month. One brain. All of them.

What You're Building
A Slack channel where you type a thought — it automatically gets embedded, classified, and stored in your database — you get a confirmation reply showing what was captured. Then an MCP server that lets any AI assistant search your brain by meaning — and write to it directly.

What You Need
About 45 minutes and zero coding experience. You'll copy and paste everything.

Services (All Free Tier)
Supabase — Your database — stores everything
OpenRouter — Your AI gateway — understands everything
Slack — Your capture interface — where you type thoughts
If You Get Stuck
Follow this guide step by step — it's designed to get you through without outside help. But if something goes sideways, Supabase has a free built-in AI assistant in every project dashboard. Look for the chat icon in the bottom-right corner. It has access to all of Supabase's documentation and can help with every Supabase-specific step in this guide.

Things it's good at:

Walking you through where to click when you can't find something in the dashboard
Fixing SQL errors if you paste in the error message
Explaining terminal commands and what their output means
Interpreting Edge Function logs when something isn't working
Explaining Supabase concepts in plain English (what's a service role key? what does Row Level Security do?)
It can't see your screen or run commands for you, but if you paste what you're seeing, it can tell you what to do next.

Two Parts
Part 1 — Capture (Steps 1–9): Slack → Edge Function → Supabase. Type a thought, it gets embedded and classified automatically.

Part 2 — Retrieval (Steps 10–13): Hosted MCP Server → Any AI. Connect Claude, ChatGPT, or any MCP client to your brain with a URL. Read and write from any tool.

After You're Done
This guide builds the system. The companion prompt pack — Open Brain: Companion Prompts — makes it useful. It includes prompts for migrating your existing AI memories into the brain, migrating an existing second brain system, discovering use cases specific to your workflow, capture templates that optimize metadata extraction, and a weekly review ritual. Finish the setup first, then grab the prompts.

Cost Breakdown
Service

Cost

Slack

Free

Supabase (free tier)

$0

Embeddings (text-embedding-3-small)

~$0.02 / million tokens

Metadata extraction (gpt-4o-mini)

~$0.15 / million input tokens

For 20 thoughts/day: roughly $0.10–0.30/month in API costs.

Credential Tracker
You're going to generate API keys, passwords, and IDs across three different services. You'll need them at specific steps later — sometimes minutes after you create them, sometimes much later. Don't trust your memory.

⚠️ Copy the block below into a text editor (Notes, TextEdit, Notepad) and fill it in as you go. Each item tells you which step generates it.

OPEN BRAIN -- CREDENTIAL TRACKER
Keep this file. Fill in as you go.

---

SUPABASE
Account email: ****\_\_\_\_****
Account password: ****\_\_\_\_****
Database password: ****\_\_\_\_**** <- Step 1
Project name: ****\_\_\_\_****
Project ref: ****\_\_\_\_**** <- Step 1
Project URL: ****\_\_\_\_**** <- Step 3
Service role key: ****\_\_\_\_**** <- Step 3

OPENROUTER
Account email: ****\_\_\_\_****
Account password: ****\_\_\_\_****
API key: ****\_\_\_\_**** <- Step 4

SLACK
Workspace name: ****\_\_\_\_****
Workspace URL: ****\_\_\_\_****
Channel name: ****\_\_\_\_****
Channel ID: ****\_\_\_\_**** <- Step 5
Bot OAuth Token: ****\_\_\_\_**** <- Step 6

GENERATED DURING SETUP
Edge Function URL: ****\_\_\_\_**** <- Step 7
MCP Access Key: ****\_\_\_\_**** <- Step 10
MCP Server URL: ****\_\_\_\_**** <- Step 11
MCP Connection URL: ****\_\_\_\_**** <- Step 11 (server URL + ?key=your-access-key)

---

Seriously — copy that now. You'll thank yourself at Step 7.

Part 1 — Capture
Step 1: Create Your Supabase Project
Supabase is your database. It stores your thoughts as raw text, vector embeddings, and structured metadata. It also gives you a REST API automatically.

Go to supabase.com and sign up (GitHub login is fastest)
Click New Project in the dashboard
Pick your organization (default is fine)
Set Project name: open-brain (or whatever you want)
Generate a strong Database password — paste into credential tracker NOW
Pick the Region closest to you
Click Create new project and wait 1–2 minutes
💡 Grab your Project ref — it's the random string in your dashboard URL: supabase.com/dashboard/project/THIS_PART. Paste it into the tracker.

Step 2: Set Up the Database
Three SQL commands, pasted one at a time. This creates your storage table, your search function, and your security policy.

Enable the Vector Extension
In the left sidebar: Database → Extensions → search for "vector" → flip pgvector ON.

Create the Thoughts Table
In the left sidebar: SQL Editor → New query → paste and Run:

-- Create the thoughts table
create table thoughts (
id uuid default gen_random_uuid() primary key,
content text not null,
embedding vector(1536),
metadata jsonb default '{}'::jsonb,
created_at timestamptz default now(),
updated_at timestamptz default now()
);

-- Index for fast vector similarity search
create index on thoughts
using hnsw (embedding vector_cosine_ops);

-- Index for filtering by metadata fields
create index on thoughts using gin (metadata);

-- Index for date range queries
create index on thoughts (created_at desc);

-- Auto-update the updated_at timestamp
create or replace function update_updated_at()
returns trigger as $$
begin
new.updated_at = now();
return new;
end;

$$
language plpgsql;

create trigger thoughts_updated_at
  before update on thoughts
  for each row
  execute function update_updated_at();



Create the Search Function
New query → paste and Run:

-- Semantic search function
create or replace function match_thoughts(
  query_embedding vector(1536),
  match_threshold float default 0.7,
  match_count int default 10,
  filter jsonb default '{}'::jsonb
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float,
  created_at timestamptz
)
language plpgsql
as
$$

begin
return query
select
t.id,
t.content,
t.metadata,
1 - (t.embedding <=> query_embedding) as similarity,
t.created_at
from thoughts t
where 1 - (t.embedding <=> query_embedding) > match_threshold
and (filter = '{}'::jsonb or t.metadata @> filter)
order by t.embedding <=> query_embedding
limit match_count;
end;

$$
;



Lock Down Security
One more new query:



-- Enable Row Level Security
alter table thoughts enable row level security;

-- Service role full access only
create policy "Service role full access"
  on thoughts
  for all
  using (auth.role() = 'service_role');



Quick Verification
Table Editor should show the thoughts table with columns: id, content, embedding, metadata, created_at, updated_at. Database → Functions should show match_thoughts.





Step 3: Save Your Connection Details
In the left sidebar: Settings (gear icon) → API. Copy these into your credential tracker:

Project URL — Listed at the top as "URL"
Service role key — Under "Project API keys" → click reveal
⚠️ Treat the service role key like a password. Anyone with it has full access to your data.




Step 4: Get an OpenRouter API Key
OpenRouter is a universal AI API gateway — one account gives you access to every major model. We're using it for embeddings and lightweight LLM metadata extraction.

Why OpenRouter instead of OpenAI directly? One account, one key, one billing relationship — and it future-proofs you for Claude, Gemini, or any other model later.

Go to openrouter.ai and sign up
Go to openrouter.ai/keys
Click Create Key, name it open-brain
Copy the key into your credential tracker immediately
Add $5 in credits under Credits (lasts months)
Step 5: Create Your Slack Capture Channel
If you don't have a Slack workspace, create one at slack.com (free tier works)
Click the + next to Channels → Create new channel
Name it "capture" (or brain, inbox, whatever feels natural)
Make it Private (recommended — this is personal)
Get the Channel ID: right-click channel → View channel details → scroll to bottom (starts with C)
Paste the Channel ID into your credential tracker
Step 6: Create the Slack App
This is the bridge between Slack and your database.

Create the App
Go to api.slack.com/apps → Create New App → From scratch
App Name: "Open Brain", select your workspace
Click Create App
Set Permissions
Left sidebar → OAuth & Permissions
Scroll to Scopes → Bot Token Scopes
Add: channels:history, groups:history, chat:write
Scroll up → Install to Workspace → Allow
Copy the Bot User OAuth Token (starts with xoxb-) into credential tracker



Add App to Channel
In Slack, open your capture channel and type: /invite @Open Brain

💡 Don't set up Event Subscriptions yet — you need the Edge Function URL first (Step 7).




Step 7: Deploy the Edge Function
This is the brains of the operation. One function receives messages from Slack, generates an embedding, extracts metadata, stores everything in Supabase, and replies with a confirmation.

💡 New to the terminal? The "terminal" is the text-based command line on your computer. On Mac, open the app called Terminal (search for it in Spotlight). On Windows, open PowerShell. Everything below gets typed there, not in your browser.



Install the Supabase CLI
💡 Mac users: If you already have Homebrew installed (you'll know — it's the thing you install with brew), use the first option. Windows users: use Scoop — Supabase recommends it over npm for Windows because it handles PATH and permissions cleanly. Linux or Mac without Homebrew: use npm.




# Mac with Homebrew
brew install supabase/tap/supabase
# Windows with Scoop (recommended)
# Install Scoop first if you don't have it:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# Then install Supabase:
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
# Linux or Mac without Homebrew
npm install -g supabase
Verify it worked:

supabase --version
Log In and Link
supabase login
supabase link --project-ref YOUR_PROJECT_REF
Replace YOUR_PROJECT_REF with the project ref from your credential tracker (Step 1).
Create the Function
supabase functions new ingest-thought
Open supabase/functions/ingest-thought/index.ts and replace its entire contents with:

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY")!;
const SLACK_BOT_TOKEN = Deno.env.get("SLACK_BOT_TOKEN")!;
const SLACK_CAPTURE_CHANNEL = Deno.env.get("SLACK_CAPTURE_CHANNEL")!;

const OPENROUTER_BASE = "https://openrouter.ai/api/v1";
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function getEmbedding(text: string): Promise<number[]> {
  const r = await fetch(`${OPENROUTER_BASE}/embeddings`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "openai/text-embedding-3-small", input: text }),
  });
  const d = await r.json();
  return d.data[0].embedding;
}

async function extractMetadata(text: string): Promise<Record<string, unknown>> {
  const r = await fetch(`${OPENROUTER_BASE}/chat/completions`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "openai/gpt-4o-mini",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: `Extract metadata from the user's captured thought. Return JSON with:
- "people": array of people mentioned (empty if none)
- "action_items": array of implied to-dos (empty if none)
- "dates_mentioned": array of dates YYYY-MM-DD (empty if none)
- "topics": array of 1-3 short topic tags (always at least one)
- "type": one of "observation", "task", "idea", "reference", "person_note"
Only extract what's explicitly there.` },
        { role: "user", content: text },
      ],
    }),
  });
  const d = await r.json();
  try { return JSON.parse(d.choices[0].message.content); }
  catch { return { topics: ["uncategorized"], type: "observation" }; }
}

async function replyInSlack(channel: string, threadTs: string, text: string): Promise<void> {
  await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: { "Authorization": `Bearer ${SLACK_BOT_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ channel, thread_ts: threadTs, text }),
  });
}

Deno.serve(async (req: Request): Promise<Response> => {
  try {
    const body = await req.json();
    if (body.type === "url_verification") {
      return new Response(JSON.stringify({ challenge: body.challenge }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    const event = body.event;
    if (!event || event.type !== "message" || event.subtype || event.bot_id
        || event.channel !== SLACK_CAPTURE_CHANNEL) {
      return new Response("ok", { status: 200 });
    }
    const messageText: string = event.text;
    const channel: string = event.channel;
    const messageTs: string = event.ts;
    if (!messageText || messageText.trim() === "") return new Response("ok", { status: 200 });

    const [embedding, metadata] = await Promise.all([
      getEmbedding(messageText),
      extractMetadata(messageText),
    ]);

    const { error } = await supabase.from("thoughts").insert({
      content: messageText,
      embedding,
      metadata: { ...metadata, source: "slack", slack_ts: messageTs },
    });

    if (error) {
      console.error("Supabase insert error:", error);
      await replyInSlack(channel, messageTs, `Failed to capture: ${error.message}`);
      return new Response("error", { status: 500 });
    }

    const meta = metadata as Record<string, unknown>;
    let confirmation = `Captured as *${meta.type || "thought"}*`;
    if (Array.isArray(meta.topics) && meta.topics.length > 0)
      confirmation += ` - ${meta.topics.join(", ")}`;
    if (Array.isArray(meta.people) && meta.people.length > 0)
      confirmation += `\nPeople: ${meta.people.join(", ")}`;
    if (Array.isArray(meta.action_items) && meta.action_items.length > 0)
      confirmation += `\nAction items: ${meta.action_items.join("; ")}`;

    await replyInSlack(channel, messageTs, confirmation);
    return new Response("ok", { status: 200 });
  } catch (err) {
    console.error("Function error:", err);
    return new Response("error", { status: 500 });
  }
});

Set Your Secrets
supabase secrets set OPENROUTER_API_KEY=your-openrouter-key-here
supabase secrets set SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
supabase secrets set SLACK_CAPTURE_CHANNEL=C0your-channel-id-here
💡 SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are automatically available inside Edge Functions — you don't need to set them.

Deploy
supabase functions deploy ingest-thought --no-verify-jwt
⚠️ Copy the Edge Function URL immediately after deployment! It looks like: https://YOUR_PROJECT_REF.supabase.co/functions/v1/ingest-thought

Step 8: Connect Slack to the Edge Function
Go to api.slack.com/apps → select your Open Brain app
Left sidebar → Event Subscriptions → toggle Enable Events ON
Paste your Edge Function URL in the Request URL field
Wait for the green checkmark ✅ Verified
Under Subscribe to bot events, add both: message.channels and message.groups
Click Save Changes (reinstall if prompted)
⚠️ You need both events. Slack treats public and private channels as separate entity types. Public channels fire message.channels, private channels fire message.groups. If you only add one, messages in the other channel type will silently fail — no error, just nothing happens. Add both so you're covered regardless of how your capture channel is configured.

Step 9: Test It
Go to your capture channel in Slack and type:

Sarah mentioned she's thinking about leaving her job to start a consulting business
Wait 5–10 seconds. You should see a threaded reply:

Captured as person_note — career, consulting
People: Sarah
Action items: Check in with Sarah about consulting plans
Then open Supabase dashboard → Table Editor → thoughts. You should see one row with your message, an embedding, and metadata.

💡 If that works, Part 1 is done. You have a working capture system.

Part 2 — Retrieval


A Quick Note on Architecture
MCP servers can run two ways: locally on your computer, or hosted in the cloud.

The local approach means installing Node.js, building a TypeScript project, and running a server process on your machine. Every AI client you connect needs the full path to that server plus your database credentials pasted into a config file. If your laptop is closed, your brain is offline. If you switch computers, you set it up again.

We're not doing that.

Your capture system already runs on Supabase — the Edge Function you deployed in Part 1 handles Slack messages without anything running on your computer. The MCP server works the same way. One more Edge Function, deployed to the same project, reachable from anywhere. Your AI clients connect with a URL. No build steps, no local dependencies, no credentials on your machine.

If you want to run locally — maybe you're a developer who prefers that, or you want to customize beyond what Edge Functions allow — the MCP TypeScript SDK with StdioServerTransport works great. The Supabase docs on deploying MCP servers cover both approaches. Everything below uses hosted.



Step 10: Create an Access Key
Your MCP server will be a public URL. The Supabase project ref in that URL is random enough that nobody will stumble onto it, but let's close the gap entirely. You'll generate a simple access key that the server checks on every request. Takes 30 seconds.

In your terminal, generate a random key:

# Mac/Linux
openssl rand -hex 32
# Windows (PowerShell)
-join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
Copy the output — it'll look something like a3f8b2c1d4e5... (64 characters). Paste it into your credential tracker under MCP Access Key.

Set it as a Supabase secret:

supabase secrets set MCP_ACCESS_KEY=your-generated-key-here
Step 11: Deploy the MCP Server
One Edge Function. Four tools: semantic search, browse recent thoughts, stats, and capture. Same deployment process as the capture function.

Create the Function
supabase functions new open-brain-mcp
Add Dependencies
Create supabase/functions/open-brain-mcp/deno.json:

{
  "imports": {
    "@hono/mcp": "npm:@hono/mcp@0.1.1",
    "@modelcontextprotocol/sdk": "npm:@modelcontextprotocol/sdk@1.24.3",
    "hono": "npm:hono@4.9.2",
    "zod": "npm:zod@4.1.13",
    "@supabase/supabase-js": "npm:@supabase/supabase-js@2.47.10"
  }
}
Write the Server
Open supabase/functions/open-brain-mcp/index.ts and replace its entire contents with:



import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPTransport } from "@hono/mcp";
import { Hono } from "hono";
import { z } from "zod";
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY")!;
const MCP_ACCESS_KEY = Deno.env.get("MCP_ACCESS_KEY")!;

const OPENROUTER_BASE = "https://openrouter.ai/api/v1";
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function getEmbedding(text: string): Promise<number[]> {
  const r = await fetch(`${OPENROUTER_BASE}/embeddings`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "openai/text-embedding-3-small",
      input: text,
    }),
  });
  if (!r.ok) {
    const msg = await r.text().catch(() => "");
    throw new Error(`OpenRouter embeddings failed: ${r.status} ${msg}`);
  }
  const d = await r.json();
  return d.data[0].embedding;
}

async function extractMetadata(text: string): Promise<Record<string, unknown>> {
  const r = await fetch(`${OPENROUTER_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "openai/gpt-4o-mini",
      response_format: { type: "json_object" },
      messages: [
        {
          role: "system",
          content: `Extract metadata from the user's captured thought. Return JSON with:
- "people": array of people mentioned (empty if none)
- "action_items": array of implied to-dos (empty if none)
- "dates_mentioned": array of dates YYYY-MM-DD (empty if none)
- "topics": array of 1-3 short topic tags (always at least one)
- "type": one of "observation", "task", "idea", "reference", "person_note"
Only extract what's explicitly there.`,
        },
        { role: "user", content: text },
      ],
    }),
  });
  const d = await r.json();
  try {
    return JSON.parse(d.choices[0].message.content);
  } catch {
    return { topics: ["uncategorized"], type: "observation" };
  }
}

// --- MCP Server Setup ---

const server = new McpServer({
  name: "open-brain",
  version: "1.0.0",
});

// Tool 1: Semantic Search
server.registerTool(
  "search_thoughts",
  {
    title: "Search Thoughts",
    description:
      "Search captured thoughts by meaning. Use this when the user asks about a topic, person, or idea they've previously captured.",
    inputSchema: {
      query: z.string().describe("What to search for"),
      limit: z.number().optional().default(10),
      threshold: z.number().optional().default(0.5),
    },
  },
  async ({ query, limit, threshold }) => {
    try {
      const qEmb = await getEmbedding(query);
      const { data, error } = await supabase.rpc("match_thoughts", {
        query_embedding: qEmb,
        match_threshold: threshold,
        match_count: limit,
        filter: {},
      });

      if (error) {
        return {
          content: [{ type: "text" as const, text: `Search error: ${error.message}` }],
          isError: true,
        };
      }

      if (!data || data.length === 0) {
        return {
          content: [{ type: "text" as const, text: `No thoughts found matching "${query}".` }],
        };
      }

      const results = data.map(
        (
          t: {
            content: string;
            metadata: Record<string, unknown>;
            similarity: number;
            created_at: string;
          },
          i: number
        ) => {
          const m = t.metadata || {};
          const parts = [
            `--- Result ${i + 1} (${(t.similarity * 100).toFixed(1)}% match) ---`,
            `Captured: ${new Date(t.created_at).toLocaleDateString()}`,
            `Type: ${m.type || "unknown"}`,
          ];
          if (Array.isArray(m.topics) && m.topics.length)
            parts.push(`Topics: ${(m.topics as string[]).join(", ")}`);
          if (Array.isArray(m.people) && m.people.length)
            parts.push(`People: ${(m.people as string[]).join(", ")}`);
          if (Array.isArray(m.action_items) && m.action_items.length)
            parts.push(`Actions: ${(m.action_items as string[]).join("; ")}`);
          parts.push(`\n${t.content}`);
          return parts.join("\n");
        }
      );

      return {
        content: [
          {
            type: "text" as const,
            text: `Found ${data.length} thought(s):\n\n${results.join("\n\n")}`,
          },
        ],
      };
    } catch (err: unknown) {
      return {
        content: [{ type: "text" as const, text: `Error: ${(err as Error).message}` }],
        isError: true,
      };
    }
  }
);

// Tool 2: List Recent
server.registerTool(
  "list_thoughts",
  {
    title: "List Recent Thoughts",
    description:
      "List recently captured thoughts with optional filters by type, topic, person, or time range.",
    inputSchema: {
      limit: z.number().optional().default(10),
      type: z.string().optional().describe("Filter by type: observation, task, idea, reference, person_note"),
      topic: z.string().optional().describe("Filter by topic tag"),
      person: z.string().optional().describe("Filter by person mentioned"),
      days: z.number().optional().describe("Only thoughts from the last N days"),
    },
  },
  async ({ limit, type, topic, person, days }) => {
    try {
      let q = supabase
        .from("thoughts")
        .select("content, metadata, created_at")
        .order("created_at", { ascending: false })
        .limit(limit);

      if (type) q = q.contains("metadata", { type });
      if (topic) q = q.contains("metadata", { topics: [topic] });
      if (person) q = q.contains("metadata", { people: [person] });
      if (days) {
        const since = new Date();
        since.setDate(since.getDate() - days);
        q = q.gte("created_at", since.toISOString());
      }

      const { data, error } = await q;

      if (error) {
        return {
          content: [{ type: "text" as const, text: `Error: ${error.message}` }],
          isError: true,
        };
      }

      if (!data || !data.length) {
        return { content: [{ type: "text" as const, text: "No thoughts found." }] };
      }

      const results = data.map(
        (
          t: { content: string; metadata: Record<string, unknown>; created_at: string },
          i: number
        ) => {
          const m = t.metadata || {};
          const tags = Array.isArray(m.topics) ? (m.topics as string[]).join(", ") : "";
          return `${i + 1}. [${new Date(t.created_at).toLocaleDateString()}] (${m.type || "??"}${tags ? " - " + tags : ""})\n   ${t.content}`;
        }
      );

      return {
        content: [
          {
            type: "text" as const,
            text: `${data.length} recent thought(s):\n\n${results.join("\n\n")}`,
          },
        ],
      };
    } catch (err: unknown) {
      return {
        content: [{ type: "text" as const, text: `Error: ${(err as Error).message}` }],
        isError: true,
      };
    }
  }
);

// Tool 3: Stats
server.registerTool(
  "thought_stats",
  {
    title: "Thought Statistics",
    description: "Get a summary of all captured thoughts: totals, types, top topics, and people.",
    inputSchema: {},
  },
  async () => {
    try {
      const { count } = await supabase
        .from("thoughts")
        .select("*", { count: "exact", head: true });

      const { data } = await supabase
        .from("thoughts")
        .select("metadata, created_at")
        .order("created_at", { ascending: false });

      const types: Record<string, number> = {};
      const topics: Record<string, number> = {};
      const people: Record<string, number> = {};

      for (const r of data || []) {
        const m = (r.metadata || {}) as Record<string, unknown>;
        if (m.type) types[m.type as string] = (types[m.type as string] || 0) + 1;
        if (Array.isArray(m.topics))
          for (const t of m.topics) topics[t as string] = (topics[t as string] || 0) + 1;
        if (Array.isArray(m.people))
          for (const p of m.people) people[p as string] = (people[p as string] || 0) + 1;
      }

      const sort = (o: Record<string, number>): [string, number][] =>
        Object.entries(o)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 10);

      const lines: string[] = [
        `Total thoughts: ${count}`,
        `Date range: ${
          data?.length
            ? new Date(data[data.length - 1].created_at).toLocaleDateString() +
              " → " +
              new Date(data[0].created_at).toLocaleDateString()
            : "N/A"
        }`,
        "",
        "Types:",
        ...sort(types).map(([k, v]) => `  ${k}: ${v}`),
      ];

      if (Object.keys(topics).length) {
        lines.push("", "Top topics:");
        for (const [k, v] of sort(topics)) lines.push(`  ${k}: ${v}`);
      }

      if (Object.keys(people).length) {
        lines.push("", "People mentioned:");
        for (const [k, v] of sort(people)) lines.push(`  ${k}: ${v}`);
      }

      return { content: [{ type: "text" as const, text: lines.join("\n") }] };
    } catch (err: unknown) {
      return {
        content: [{ type: "text" as const, text: `Error: ${(err as Error).message}` }],
        isError: true,
      };
    }
  }
);

// Tool 4: Capture Thought
server.registerTool(
  "capture_thought",
  {
    title: "Capture Thought",
    description:
      "Save a new thought to the Open Brain. Generates an embedding and extracts metadata automatically. Use this when the user wants to save something to their brain directly from any AI client — notes, insights, decisions, or migrated content from other systems.",
    inputSchema: {
      content: z.string().describe("The thought to capture — a clear, standalone statement that will make sense when retrieved later by any AI"),
    },
  },
  async ({ content }) => {
    try {
      const [embedding, metadata] = await Promise.all([
        getEmbedding(content),
        extractMetadata(content),
      ]);

      const { error } = await supabase.from("thoughts").insert({
        content,
        embedding,
        metadata: { ...metadata, source: "mcp" },
      });

      if (error) {
        return {
          content: [{ type: "text" as const, text: `Failed to capture: ${error.message}` }],
          isError: true,
        };
      }

      const meta = metadata as Record<string, unknown>;
      let confirmation = `Captured as ${meta.type || "thought"}`;
      if (Array.isArray(meta.topics) && meta.topics.length)
        confirmation += ` — ${(meta.topics as string[]).join(", ")}`;
      if (Array.isArray(meta.people) && meta.people.length)
        confirmation += ` | People: ${(meta.people as string[]).join(", ")}`;
      if (Array.isArray(meta.action_items) && meta.action_items.length)
        confirmation += ` | Actions: ${(meta.action_items as string[]).join("; ")}`;

      return {
        content: [{ type: "text" as const, text: confirmation }],
      };
    } catch (err: unknown) {
      return {
        content: [{ type: "text" as const, text: `Error: ${(err as Error).message}` }],
        isError: true,
      };
    }
  }
);

// --- Hono App with Auth Check ---

const app = new Hono();

app.all("*", async (c) => {
  // Accept access key via header OR URL query parameter
  const provided = c.req.header("x-brain-key") || new URL(c.req.url).searchParams.get("key");
  if (!provided || provided !== MCP_ACCESS_KEY) {
    return c.json({ error: "Invalid or missing access key" }, 401);
  }

  const transport = new StreamableHTTPTransport();
  await server.connect(transport);
  return transport.handleRequest(c);
});

Deno.serve(app.fetch);


Deploy
supabase functions deploy open-brain-mcp --no-verify-jwt
Your MCP server is now live at:

https://YOUR_PROJECT_REF.supabase.co/functions/v1/open-brain-mcp
Replace YOUR_PROJECT_REF with the project ref from your credential tracker (Step 1). Paste the full URL into your credential tracker as the MCP Server URL.

Now build your MCP Connection URL by adding your access key to the end:

https://YOUR_PROJECT_REF.supabase.co/functions/v1/open-brain-mcp?key=your-access-key-from-step-10
Paste this into your credential tracker as the MCP Connection URL. This is what you'll give to AI clients that support remote MCP — one URL, no extra config.

💡 That's it. No npm install, no TypeScript build, no local server to keep running. It's deployed alongside your capture function and runs on Supabase's infrastructure.



Step 12: Connect to Your AI
You need your MCP Connection URL from the credential tracker — the one with ?key= at the end.

Claude Desktop
Open Claude Desktop → Settings → Connectors
Click Add custom connector
Name: Open Brain
Remote MCP server URL: paste your MCP Connection URL (the one ending in ?key=your-access-key)
Click Add
That's it. Start a new conversation, and Claude will have access to your Open Brain tools. You can enable or disable it per conversation via the "+" button → Connectors.

💡 No JSON config files. No Node.js. No terminal. If you had trouble with earlier versions of this guide, this is the fix.

ChatGPT
Requires a paid ChatGPT plan (Plus, Pro, Business, Enterprise, or Edu) and works on the web at chatgpt.com. Not available on mobile.

Enable Developer Mode (one-time setup):


$$
