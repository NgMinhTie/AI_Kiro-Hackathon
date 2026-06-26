# ⚡ AutoSpec — AI Agent That Writes Its Own Spec, Builds, and Tests

## AWS Kiro Hackathon · Challenge 8 (Stretch)

---

## 🎯 The Problem

**Persona:** Priya, a Product Manager at a consultancy.

- She can describe what she wants in plain English
- She has NO engineering background
- She needs a working prototype — documented, coded, tested — to demo to clients **the same day**

> "I just want to type what I need and get back something that works."

---

## 💡 Our Solution: AutoSpec

A **multi-agent AI pipeline** that takes a 2-3 sentence brief and autonomously produces:

1. ✅ A structured specification (numbered requirements + acceptance criteria)
2. ✅ Working Python code
3. ✅ A passing test suite with coverage
4. ✅ A spec-to-code alignment verdict

**Zero human intervention mid-run.**

---

## 🏗️ Architecture: 4 Specialized Agents

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
│  SPEC   │────▶│  BUILD  │────▶│  TEST   │────▶│  REVIEW  │
│  Agent  │     │  Agent  │     │  Agent  │     │  Agent   │
└─────────┘     └─────────┘     └─────────┘     └──────────┘
     │                ▲                                │
     │                │         NOT ALIGNED            │
     │                └────────────────────────────────┘
     │                    Self-Correcting Loop (max 3)
     ▼
  Brief → Spec → Code → Tests → Verdict
```

| Agent | Input | Output |
|-------|-------|--------|
| **Spec Agent** | Plain English brief | Numbered requirements + Given/When/Then criteria + edge cases |
| **Build Agent** | Spec Document | Single Python module (pure functions, documented) |
| **Test Agent** | Spec + Code | pytest suite (1 test per criterion) — **runs for real** |
| **Review Agent** | Spec + Code + Test Report | ALIGNED / NOT ALIGNED + exact gaps |

---

## 🔄 The Innovation: Self-Correcting Loop

When the Review Agent finds gaps:

1. It identifies **exactly which acceptance criteria** are not met
2. It feeds the gaps back to the Build Agent
3. The pipeline re-runs Build → Test → Review
4. Up to **3 automatic retries** — no human needed

> "The pipeline doesn't just fail — it **fixes itself.**"

---

## 🖥️ Live Demo

**Single command:** `python3 app.py` → Open browser → http://localhost:5000

### What you'll see:

1. **Type a brief** (or load the built-in tip-calculator demo)
2. **Click Run** → Watch 4 agents light up in sequence
3. **Live streaming** of each agent's output via Server-Sent Events
4. **Real test execution** — pytest actually runs, coverage is measured
5. **ALIGNED verdict** with 100% coverage

### Self-Correction Demo:

- Click **"Run with Self-Correction Demo"**
- Watch: Review says NOT ALIGNED → shows gaps → retries → succeeds
- The retry loop is **visible in real-time**

---

## 📊 Results (Sample Run — Tip Calculator)

| Metric | Value |
|--------|-------|
| Requirements generated | 6 |
| Acceptance criteria | 6 (Given/When/Then) |
| Edge cases identified | 6 |
| Tests written | 8 |
| Tests passed | **8/8** |
| Coverage | **100%** |
| Verdict | **✅ ALIGNED** |
| Total time | ~8 seconds |

---

## 🛠️ Built With Kiro

We used Kiro's **spec-driven development** to build AutoSpec itself:

- **requirements.md** — 13 formal requirements in EARS format
- **design.md** — Full architecture, mermaid diagrams, 26 correctness properties
- **tasks.md** — Incremental implementation plan with dependency graph

> "We used Kiro's spec workflow to build a tool that DOES spec-driven development. It's spec-ception."

---

## 🏆 Why This Should Win

| Judging Criterion | How We Score |
|---|---|
| **Spec quality (25%)** | 13 EARS requirements, Given/When/Then criteria, glossary, full traceability |
| **Working demo (30%)** | Live web UI, real pytest execution, 100% coverage, downloadable artifacts |
| **Innovation (20%)** | Self-correcting retry loop, live SSE streaming, web dashboard, 4-agent architecture |
| **Pitch (25%)** | Visual relay in browser — you're watching it now |

---

## 📦 Deliverables Checklist

- [x] **Live end-to-end pipeline demo** → Web UI at localhost:5000
- [x] **Generated spec document** → `artifacts/<run_id>/spec_document.md`
- [x] **Agent handoff diagram** → Animated in UI + mermaid in design.md
- [x] **Kiro spec + agent orchestration design** → `.kiro/specs/autospec-pipeline/`
- [x] **Generated code + passing test results** → Real pytest, 8/8 passed, 100% coverage
- [x] **3-min pitch** → This presentation + live demo

---

## 🚀 Key Differentiators

1. **Tests are REAL** — not mocked. Actual pytest subprocess with coverage parsing.
2. **Self-correcting** — the pipeline identifies gaps and fixes them automatically.
3. **Web UI** — judges see the relay live, not a terminal dump.
4. **Spec-ception** — Kiro built a tool that does what Kiro does.
5. **Offline-resilient** — deterministic fallback means the demo never fails.

---

## ⏱️ 3-Minute Pitch Script

**[0:00 - 0:30] The Hook**
> "What if a PM could type three sentences and get back a documented, tested, working prototype? No engineers needed. No waiting. Just AI agents building software for you."

**[0:30 - 1:00] The Architecture**
> "AutoSpec is four AI agents in a relay. Spec Agent writes the requirements. Build Agent writes the code. Test Agent runs real tests. And Review Agent checks alignment. If something's wrong — it loops back and fixes itself."

**[1:00 - 2:30] The Demo**
> *[Show web UI, click Run, narrate as agents light up]*
> "Watch — Spec Agent just wrote 6 requirements with acceptance criteria... Build Agent generated a Python module... Test Agent is running pytest right now — 8 tests, all passing, 100% coverage... and Review says ALIGNED."
>
> *[Click Self-Correction Demo]*
> "Now watch what happens when something's wrong — Review found 2 gaps, it's feeding them back to Build... Build is fixing it... running tests again... and now it's ALIGNED. Self-correcting, no human needed."

**[2:30 - 3:00] The Close**
> "We built this with Kiro's spec-driven workflow — 13 requirements, full design doc, implementation plan. And the tool we built does exactly what Kiro does: takes plain English and turns it into working, tested software. That's AutoSpec."

---

## Thank You! 🙏

**Team:** [Your Team Name]

**Tech Stack:** Python · Flask · pytest · Kiro · SSE

**Try it:** `python3 app.py` → http://localhost:5000
