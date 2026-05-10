## Failures Are Data, Not Just Problems

Every AI agent failure carries information about system weaknesses, edge cases, and assumptions that do not hold in production. Teams that treat failures as one-off bugs to squash miss the pattern. Teams that run structured post-mortems build increasingly resilient systems because each incident reduces the probability of the next.

For AI agents specifically, post-mortems are even more valuable because the failure modes are novel — hallucinations, prompt injection, tool misuse, and multi-step reasoning failures do not appear in traditional software engineering playbooks.

## Incident Classification Framework

Not every error deserves a post-mortem. A classification system triages failures by severity and novelty.

    flowchart TD
        START["Post-Mortem Analysis for AI Agent Failures: Learn…"] --> A
        A["Failures Are Data, Not Just Problems"]
        A --> B
        B["Incident Classification Framework"]
        B --> C
        C["Automated Incident Capture"]
        C --> D
        D["Structured Root Cause Analysis"]
        D --> E
        E["Action Item Tracking"]
        E --> F
        F["Incident Knowledge Base"]
        F --> G
        G["Generating Post-Mortem Reports"]
        G --> H
        H["FAQ"]
        H --> DONE["Key Takeaways"]
        style START fill:#4f46e5,stroke:#4338ca,color:#fff
        style DONE fill:#059669,stroke:#047857,color:#fff

    from dataclasses import dataclass, field
    from datetime import datetime
    from enum import Enum
    from typing import Optional

    class IncidentSeverity(Enum):
        SEV1 = "sev1"  # Complete service outage or data loss
        SEV2 = "sev2"  # Major feature broken, many users affected
        SEV3 = "sev3"  # Minor feature broken, workaround exists
        SEV4 = "sev4"  # Cosmetic or low-impact issue

    class IncidentCategory(Enum):
        LLM_HALLUCINATION = "llm_hallucination"
        LLM_REFUSAL = "llm_refusal"
        TOOL_FAILURE = "tool_failure"
        PROMPT_INJECTION = "prompt_injection"
        TIMEOUT = "timeout"
        RATE_LIMIT = "rate_limit"
        DATA_CORRUPTION = "data_corruption"
        BUSINESS_LOGIC = "business_logic"
        INFRASTRUCTURE = "infrastructure"

    @dataclass
    class Incident:
        id: str
        title: str
        severity: IncidentSeverity
        category: IncidentCategory
        description: str
        timeline: list[dict] = field(default_factory=list)
        root_cause: str = ""
        contributing_factors: list[str] = field(default_factory=list)
        action_items: list[dict] = field(default_factory=list)
        created_at: datetime = field(default_factory=datetime.utcnow)
        resolved_at: Optional[datetime] = None
        post_mortem_completed: bool = False

## Automated Incident Capture

Instead of relying on engineers to manually file incidents, instrument the agent pipeline to automatically capture and classify failures.

    import traceback
    import uuid
    import json

    class IncidentCapture:
        def __init__(self):
            self.incidents: list[Incident] = []

        def capture(
            self, error: Exception, context: dict, severity: IncidentSeverity = None,
        ) -> Incident:
            category = self._classify_error(error, context)
            if severity is None:
                severity = self._estimate_severity(error, category, context)

            incident = Incident(
                id=str(uuid.uuid4())[:8],
                title=f"{category.value}: {type(error).__name__}",
                severity=severity,
                category=category,
                description=str(error),
                timeline=[
                    {
                        "time": datetime.utcnow().isoformat(),
                        "event": "incident_detected",
                        "details": {
                            "error_type": type(error).__name__,
                            "error_message": str(error),
                            "stack_trace": traceback.format_exc(),
                            "context": context,
                        },
                    }
                ],
            )
            self.incidents.append(incident)
            return incident

        def _classify_error(self, error: Exception, context: dict) -> IncidentCategory:
            error_str = str(error).lower()

            if "rate limit" in error_str or "429" in error_str:
                return IncidentCategory.RATE_LIMIT
            if "timeout" in error_str or isinstance(error, TimeoutError):
                return IncidentCategory.TIMEOUT
            if context.get("tool_name"):
                return IncidentCategory.TOOL_FAILURE
            if "refused" in error_str or "cannot assist" in error_str:
                return IncidentCategory.LLM_REFUSAL
            return IncidentCategory.INFRASTRUCTURE

        def _estimate_severity(
            self, error: Exception, category: IncidentCategory, context: dict,
        ) -> IncidentSeverity:
            if category == IncidentCategory.DATA_CORRUPTION:
                return IncidentSeverity.SEV1
            if category in (IncidentCategory.PROMPT_INJECTION, IncidentCategory.BUSINESS_LOGIC):
                return IncidentSeverity.SEV2
            if context.get("user_facing", False):
                return IncidentSeverity.SEV3
            return IncidentSeverity.SEV4

## Structured Root Cause Analysis

The "5 Whys" technique works well for AI agent failures. Automate the template to ensure consistent analysis.

See AI Voice Agents Handle Real Calls

Book a free demo or calculate how much you can save with AI voice automation.

    @dataclass
    class RootCauseAnalysis:
        incident_id: str
        whys: list[str] = field(default_factory=list)
        root_cause: str = ""
        is_novel: bool = False
        similar_incidents: list[str] = field(default_factory=list)

    class RCAEngine:
        def __init__(self, knowledge_base: "IncidentKnowledgeBase"):
            self.kb = knowledge_base

        def create_rca(self, incident: Incident) -> RootCauseAnalysis:
            similar = self.kb.find_similar(incident)
            rca = RootCauseAnalysis(
                incident_id=incident.id,
                similar_incidents=[s.id for s in similar],
                is_novel=len(similar) == 0,
            )
            return rca

        def complete_rca(self, rca: RootCauseAnalysis, whys: list[str], root_cause: str):
            rca.whys = whys
            rca.root_cause = root_cause

## Action Item Tracking

Post-mortems without follow-through are theater. Track action items with owners and deadlines.

    @dataclass
    class ActionItem:
        id: str
        incident_id: str
        description: str
        owner: str
        priority: str  # P0, P1, P2
        deadline: Optional[datetime] = None
        status: str = "open"  # open, in_progress, completed
        completed_at: Optional[datetime] = None

    class ActionTracker:
        def __init__(self):
            self.items: list[ActionItem] = []

        def add(self, incident_id: str, description: str,
                owner: str, priority: str, deadline: datetime = None) -> ActionItem:
            item = ActionItem(
                id=str(uuid.uuid4())[:8],
                incident_id=incident_id,
                description=description,
                owner=owner,
                priority=priority,
                deadline=deadline,
            )
            self.items.append(item)
            return item

        def overdue(self) -> list[ActionItem]:
            now = datetime.utcnow()
            return [
                item for item in self.items
                if item.status == "open"
                and item.deadline
                and item.deadline < now
            ]

        def completion_rate(self) -> float:
            if not self.items:
                return 0.0
            completed = sum(1 for i in self.items if i.status == "completed")
            return completed / len(self.items)

## Incident Knowledge Base

The knowledge base stores past incidents and enables pattern matching to detect recurring issues.

    class IncidentKnowledgeBase:
        def __init__(self):
            self.incidents: list[Incident] = []
            self.patterns: dict[str, list[str]] = {}

        def add_incident(self, incident: Incident):
            self.incidents.append(incident)
            key = f"{incident.category.value}:{incident.severity.value}"
            if key not in self.patterns:
                self.patterns[key] = []
            self.patterns[key].append(incident.id)

        def find_similar(self, incident: Incident) -> list[Incident]:
            return [
                i for i in self.incidents
                if i.category == incident.category
                and i.id != incident.id
            ]

        def recurring_patterns(self, min_occurrences: int = 3) -> list[dict]:
            recurring = []
            for key, ids in self.patterns.items():
                if len(ids) >= min_occurrences:
                    category, severity = key.split(":")
                    recurring.append({
                        "category": category,
                        "severity": severity,
                        "count": len(ids),
                        "incident_ids": ids,
                    })
            return sorted(recurring, key=lambda x: x["count"], reverse=True)

        def stats(self) -> dict:
            from collections import Counter
            categories = Counter(i.category.value for i in self.incidents)
            severities = Counter(i.severity.value for i in self.incidents)
            return {
                "total": len(self.incidents),
                "by_category": dict(categories),
                "by_severity": dict(severities),
                "recurring_patterns": len(self.recurring_patterns()),
            }

## Generating Post-Mortem Reports

Combine all the components into a structured, readable report.

    def generate_post_mortem(
        incident: Incident,
        rca: RootCauseAnalysis,
        actions: list[ActionItem],
    ) -> str:
        report = f"""# Post-Mortem: {incident.title}

    **Incident ID:** {incident.id}
    **Severity:** {incident.severity.value}
    **Category:** {incident.category.value}
    **Created:** {incident.created_at.isoformat()}
    **Resolved:** {incident.resolved_at.isoformat() if incident.resolved_at else "Ongoing"}

    ## Description
    {incident.description}

    ## Timeline
    """
        for event in incident.timeline:
            report += f"- **{event['time']}**: {event['event']}\n"

        report += f"""
    ## Root Cause Analysis (5 Whys)
    """
        for i, why in enumerate(rca.whys, 1):
            report += f"{i}. {why}\n"

        report += f"""
    **Root Cause:** {rca.root_cause}
    **Novel incident:** {"Yes" if rca.is_novel else "No"}
    **Similar past incidents:** {', '.join(rca.similar_incidents) or "None"}

    ## Action Items
    """
        for item in actions:
            status_marker = "x" if item.status == "completed" else " "
            report += f"- [{status_marker}] [{item.priority}] {item.description} (Owner: {item.owner})\n"

        return report

## FAQ

### How do I decide which incidents warrant a full post-mortem?

Run full post-mortems for all SEV1 and SEV2 incidents, all novel failure modes regardless of severity, and any incident that a customer reported. For SEV3 and SEV4 incidents that match existing patterns, a lightweight review (verify the pattern, confirm existing action items are progressing) is sufficient.

### How do I prevent post-mortems from becoming blame sessions?

Establish a blameless culture by focusing the analysis on system factors, not individual decisions. Use language like "the system allowed" instead of "the engineer caused." The 5 Whys technique naturally shifts focus toward systemic root causes. Document the process, not the person — future readers need to understand what the system did, not who was on call.

### Should AI agent post-mortems differ from traditional software post-mortems?

Yes, in two key ways. First, add a "model behavior" section that captures what the LLM said or did that was unexpected — this data improves prompts and guardrails. Second, track whether the failure was deterministic (it will always happen with this input) or probabilistic (it happens some percentage of the time). Probabilistic failures require statistical testing to verify fixes, not just a single successful test run.

---


#PostMortem #IncidentAnalysis #RootCauseAnalysis #AIAgents #Python #AgenticAI #LearnAI #AIEngineering
