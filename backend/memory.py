"""
Memory: Manages the agent's short-term context.
Stores the original topic, sub-questions, and per-question findings.
Passed into each LLM call to maintain continuity.
"""

from dataclasses import dataclass, field

@dataclass
class AgentMemory:
    topic: str
    sub_questions: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)

    def add_finding(self, question: str, summaries: list[dict]):
        self.findings.append({
            "question": question,
            "summaries": summaries,
        })

    def to_context_string(self) -> str:
        """Serialize memory to a string for LLM context injection."""
        lines = [f"Research Topic: {self.topic}", ""]
        for i, finding in enumerate(self.findings, 1):
            lines.append(f"Sub-question {i}: {finding['question']}")
            for s in finding["summaries"]:
                lines.append(f"  - {s['summary']} (source: {s['url']})")
            lines.append("")
        return "\n".join(lines)
