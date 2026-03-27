# Cheatsheet — Claude Certified Architect (CCA) Foundations

Quick reference for the most frequently tested concepts on the exam.

---

## Exam Distribution

| Domain | Weight |
|--------|--------|
| Agentic Architecture & Orchestration | 27% |
| Claude Code Configuration & Workflows | 20% |
| Prompt Engineering & Structured Output | 20% |
| Tool Design & MCP Integration | 18% |
| Context Management & Reliability | 15% |

---

## Concept #1: Programmatic Enforcement vs. Prompt Guidance

**Rule:** When something MUST happen without exception, use code. Not prompts.

```
✅ Programmatic: verify identity BEFORE executing a refund
❌ Prompt: "always verify identity before a refund"
```

Prompts have a non-zero failure rate. In production, that is not acceptable.

---

## Concept #2: Agentic Loop

```python
while True:
    response = client.messages.create(...)
    
    if response.stop_reason == "end_turn":
        break  # ✅ Stop here
    
    if response.stop_reason == "tool_use":
        # Execute tools and return results
        ...
```

❌ DO NOT: detect loop end by text content
❌ DO NOT: use an iteration counter as the primary stop mechanism

---

## Concept #3: Subagents Do Not Inherit Context

In multi-agent systems, EACH subagent receives only what you explicitly pass it.

```
Orchestrator               Subagent
────────────────           ──────────────────────────────
full history          →    ONLY what you pass in the prompt
                           No shared memory
```

---

## Concept #4: Tool Descriptions Are the Routing Mechanism

The description is what Claude uses to decide which tool to call.

```python
# ❌ Vague description — Claude will guess
{"name": "search", "description": "Search for information"}

# ✅ Precise description — Claude routes correctly
{
    "name": "search_web",
    "description": (
        "Search for current information on the internet. "
        "Use for: recent news, current prices, events. "
        "NOT for: internal documents, historical company data."
    )
}
```

---

## Concept #5: Batch API vs. Real-time API

| | Batch API | Real-time API |
|-|-----------|---------------|
| Cost | 50% less | Normal price |
| SLA | Up to 24 hrs, no guarantee | Immediate |
| Use for | Nightly reports, audits | Blocking workflows |

**Rule:** The choice is NOT about cost — it's about latency and blocking.

---

## Common Exam Traps

| What seems correct | Why it's wrong |
|--------------------|----------------|
| Few-shot examples to order tools | Ordering is a compliance concern → use programmatic prerequisites |
| Self-reported confidence for escalation | LLMs poorly calibrate confidence in hard cases |
| Batch API to save on everything | No SLA; blocking workflows need real-time |
| Larger context window = better attention | Context window ≠ quality of attention |
| Return empty on subagent failure | Suppresses errors → orchestrator cannot recover |
| Give all tools to all agents | Degrades selection; use 4-5 tools per agent |

---

## The 6 Exam Scenarios (study all — only 4 appear)

1. Customer Support Resolution Agent
2. Code Generation with Claude Code
3. Multi-Agent Research System
4. Developer Productivity with Claude
5. Claude Code for CI/CD
6. Structured Data Extraction

---

## Resources

- https://docs.claude.com
- https://anthropic.skilljar.com
- https://claudecertifications.com
