=== STATUS REPORT: HYBRID VECTOR NATIVE ===

When reporting status updates, use the Hybrid Protocol to encode progress, blockers, and completion states.
Use Vector Native for Status/Routing and Verbatim Strings for Critical Context.

Format

Logic Layer:   ●status|phase:name|state:value

Detail Layer:  ⊕metric|key:value|⊕blocker|type:issue

Payload Layer: "Verbatim context, error messages, or critical details"

Examples

1. Progress Update (Executor -> Architect)

●status|phase:implementation|state:in_progress|progress:60
⊕metric|files_modified:12|tests_passing:8/10
"Refactored authentication module, 2 integration tests failing due to Redis timeout configuration."

2. Blocker Report (Debugger -> Planner)

●status|phase:debugging|state:blocked|severity:high
⊕blocker|type:external_dependency|service:redis
⊕metric|retry_count:43|error_rate:100
"Redis connection pool exhausted. All requests timing out after 5s. Need infrastructure review."

3. Completion Notice (Executor -> Auditor)

●status|phase:verification|state:complete|success:true
⊕metric|files_verified:15|linter_errors:0|tests_passing:10/10
"All verification checks passed. Ready for review."

4. Partial Success (Widget Agent -> Orchestrator)

●status|phase:execution|state:partial|success:true|warnings:2
⊕metric|artifacts_created:3|artifacts_failed:1
⊕warning|type:validation|artifact_id:abc123
"Widget executed successfully but artifact validation failed for email template. Missing required field 'subject'."

Rules

Status is Vector: Use symbols (●, ⊕) for all state, progress, and categorization.

Context is String: Use exact quotes "..." for error messages, critical insights, or specific details.

No Yapping: Never use conversational filler ("I am working on...", "The status is...").

One status per report.

States: pending, in_progress, blocked, complete, failed, partial

