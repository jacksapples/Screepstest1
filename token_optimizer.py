import json
from datetime import datetime
from typing import Optional, Literal

class ContextCompactor:
    """Compress conversation history when approaching token limits."""

    def __init__(self, token_threshold: int = 4000, keep_last_turns: int = 3):
        self.token_threshold = token_threshold
        self.keep_last_turns = keep_last_turns

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate: 1 token ≈ 4 characters."""
        return len(text) // 4

    def compact_history(self, messages: list) -> dict:
        """Compress old messages into a dense summary."""
        if len(messages) <= self.keep_last_turns:
            return {"compacted": False, "messages": messages}

        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)

        if total_tokens < self.token_threshold:
            return {"compacted": False, "messages": messages}

        recent = messages[-self.keep_last_turns:]
        old = messages[:-self.keep_last_turns]

        summary = self._create_summary(old)
        compacted = [{"role": "system", "content": f"[COMPACTED HISTORY]\n{summary}"}] + recent

        return {
            "compacted": True,
            "original_turns": len(messages),
            "compacted_turns": len(compacted),
            "tokens_saved": total_tokens - sum(self.estimate_tokens(m.get("content", "")) for m in compacted),
            "messages": compacted
        }

    def _create_summary(self, messages: list) -> str:
        """Extract key facts from message sequence."""
        facts = []
        for msg in messages:
            content = msg.get("content", "")
            if len(content) > 50:
                facts.append(content[:100] + "...")
        return " | ".join(facts[:5])

class ModelRouter:
    """Route tasks to appropriate Claude model based on complexity."""

    ROUTING_MATRIX = {
        "haiku": {
            "triggers": ["format", "rename", "quick", "lookup", "simple", "repetitive"],
            "cost_multiplier": 1.0,
            "max_context": 200000
        },
        "sonnet": {
            "triggers": ["refactor", "test", "explain", "moderate", "analysis", "typical"],
            "cost_multiplier": 3.0,
            "max_context": 200000
        },
        "opus": {
            "triggers": ["complex", "architecture", "multi-file", "deep", "critical", "reasoning"],
            "cost_multiplier": 15.0,
            "max_context": 200000
        }
    }

    def route(self, task_description: str, context_size: int = 0) -> dict:
        """Determine optimal model for task."""
        lower_task = task_description.lower()
        scores = {}

        for model, config in self.ROUTING_MATRIX.items():
            score = sum(1 for trigger in config["triggers"] if trigger in lower_task)
            scores[model] = score

        selected = max(scores, key=scores.get) if max(scores.values()) > 0 else "sonnet"

        return {
            "recommended_model": selected,
            "confidence": max(scores.values()) / len(self.ROUTING_MATRIX[selected]["triggers"]),
            "estimated_cost_multiplier": self.ROUTING_MATRIX[selected]["cost_multiplier"],
            "reasoning": f"Task matched {scores[selected]} trigger(s) for {selected.upper()}",
            "all_scores": scores
        }

class TokenOptimizer:
    """Master orchestrator combining routing and compaction."""

    def __init__(self):
        self.compactor = ContextCompactor(token_threshold=4000, keep_last_turns=3)
        self.router = ModelRouter()

    def optimize_request(self, task: str, messages: list) -> dict:
        """Full optimization pipeline."""
        route_decision = self.router.route(task)
        compaction_result = self.compactor.compact_history(messages)

        return {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "routing": route_decision,
            "compaction": compaction_result,
            "optimized_messages": compaction_result["messages"],
            "token_savings_estimate": compaction_result.get("tokens_saved", 0),
            "recommended_action": f"Use {route_decision['recommended_model'].upper()} model with {len(compaction_result['messages'])} message turns"
        }

# Quick usage example
if __name__ == "__main__":
    optimizer = TokenOptimizer()

    sample_messages = [
        {"role": "user", "content": "First question about cloud security"},
        {"role": "assistant", "content": "Long answer about cloud security best practices..."},
        {"role": "user", "content": "Follow-up question"},
        {"role": "assistant", "content": "Another detailed response..."},
    ]

    result = optimizer.optimize_request("refactor security policy document", sample_messages)
    print(json.dumps(result, indent=2))
