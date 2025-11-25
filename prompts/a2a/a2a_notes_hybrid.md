=== A2A NOTES: HYBRID VECTOR NATIVE ===

When writing A2A notes, use the Hybrid Protocol to prevent semantic drift.
Use Vector Native for State/Routing and Verbatim Strings for Payload/Context.

Format

Logic Layer:   ●operation|param:value

Detail Layer:  ⊕detail|key:value

Payload Layer: "Verbatim content, instructions, or data strings"

Examples

1. Task Handoff (Architect -> Builder)

●handoff|from:architect|to:builder|priority:high
⊕constraint|framework:react|style:minimalist
"Use the 'Glassmorphism' design language but keep accessibility scores above 95."

2. Analysis Result (Researcher -> Writer)

●insight|source:user_interviews|sentiment:negative
⊕pattern|frequency:high|impact:churn
"Users feel the dashboard is 'lying to them' because of the latency in data sync."

3. Security Alert (Scanner -> Patcher)

●alert|type:vulnerability|severity:critical
⊕location|file:auth.ts|line:45
"Input validation is missing on the 'username' field, allowing SQL injection."

Rules

Logic is Vector: Use symbols (●, ⊕) for all routing, state, and categorization.

Content is String: Use exact quotes "..." for prompt injections, specific insights, or raw data.

No Yapping: Never use conversational filler ("I have found...", "Here is the data...").

One operation per line.