# Building with the Claude API

Learning repository for the **Building with the Claude API** course by [Anthropic Academy](https://anthropic.skilljar.com/).

Preparation for the **Claude Certified Architect (CCA) — Foundations** certification.

---

## Repository Structure

```
building-with-the-claude-api-course/
├── notebooks/
│   ├── 01-basics/              # First API calls, messages, roles
│   ├── 02-tool-use/            # Tool use, function calling
│   ├── 03-agentic-loop/        # Agentic loop, stop_reason, iterations
│   ├── 04-multi-agent/         # Multi-agent systems, orchestrator + subagents
│   ├── 05-structured-outputs/  # Structured JSON, data extraction
│   └── 06-context-management/  # Context management, window, "lost in the middle"
├── src/
│   └── utils.py                # Reusable helpers
├── resources/                  # Notes, cheatsheets, and reference material
├── .env.example                # Required environment variables
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/esjimenezro/building-with-the-claude-api-course.git
cd building-with-the-claude-api-course
```

### 2. Create a virtual environment and install dependencies

```bash
uv sync
source .venv/bin/activate        # macOS/Linux
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

Get your API key at: https://console.anthropic.com/

---

## Modules

| # | Module | Exam Domain | Status |
|---|--------|-------------|--------|
| 01 | Basics: messages, roles, system prompt | Context Management (15%) | ✅ |
| 02 | Tool use: design and routing | Tool Design & MCP (18%) | ⬜ |
| 03 | Agentic loop: stop_reason, iterations | Agentic Architecture (27%) | ⬜ |
| 04 | Multi-agent: orchestrator + subagents | Agentic Architecture (27%) | ⬜ |
| 05 | Structured outputs: JSON extraction | Prompt Engineering (20%) | ⬜ |
| 06 | Context management: window and limits | Context Management (15%) | ⬜ |

---

## Resources

- [Anthropic Academy](https://anthropic.skilljar.com/)
- [Official Claude Documentation](https://docs.claude.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [Claude Certifications — practice exams](https://claudecertifications.com/)

---

## Author

**Esteban Jimenez** — Senior Data Scientist @ EPAM NEORIS
