# Hard Instructions for All Claude Sessions

## Token Optimizer — Mandatory Hard Skill

The file `token_optimizer.py` in this repository defines a **mandatory hard skill** that must be applied in every conversation with any Claude model.

### What It Does

- **ContextCompactor**: When conversation history exceeds ~4000 tokens, compress older turns into a dense summary, keeping only the 3 most recent turns in full.
- **ModelRouter**: Route tasks to the appropriate Claude model based on keyword triggers:
  - **Haiku** — format, rename, quick, lookup, simple, repetitive tasks
  - **Sonnet** — refactor, test, explain, moderate, analysis, typical tasks
  - **Opus** — complex, architecture, multi-file, deep, critical, reasoning tasks
- **TokenOptimizer**: Combines both into a single optimization pipeline.

### Hard Rules

1. **Always apply model routing logic** before starting any task. Use the `ROUTING_MATRIX` triggers to determine which Claude model tier is appropriate.
2. **Always monitor context size**. If the conversation is growing long, apply compaction logic — summarize older turns, keep the last 3 full turns.
3. **Never use a heavier model** (Opus) for tasks that clearly match Haiku or Sonnet triggers.
4. **Never waste context** — strip redundant content, old summaries, and repeated instructions before sending to the model.

### Reference Implementation

See `token_optimizer.py` for the full implementation. This logic should be treated as a persistent behavioral constraint across all sessions.
