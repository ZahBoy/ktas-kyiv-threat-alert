# KSE Agentic AI School Application Essay

**Application Question:** *"Додай есе до 250 слів англійською мовою (що ти робив, де модель помилилась, як ти змінив підхід і що забрав із цього досвіду)"*  
**Word Count:** 229 words (limit: strictly under 250 words)

---

### Essay Text

When building AI solutions for wartime Ukraine, I focused on high-stakes, real-world utility: an automated accessibility auditor checking architectural blueprints for wounded veterans, and the Kyiv Threat Alert System (KTAS) to combat alert fatigue.

Initially, foundation models failed at foundational engineering. In the accessibility project, LLMs generated superficial promotional fluff and hallucinated spatial geometry, miscalculating ramp inclines and wheelchair turning radiuses. In KTAS, the model proposed a naive Telegram bot architecture, completely overlooking Telegram's 30 message-per-second rate limit, Android Doze mode, and the fatal inability of bots to pierce nighttime Do Not Disturb settings. Worse, it suggested centralized GPS storage, creating a severe wartime security vulnerability.

I pivoted from open-ended conversational prompting to agentic systems engineering. First, I used structured brainstorming and humanizer constraints to eliminate AI slop and isolate core user problems. Second, I decomposed reasoning tasks into deterministic fast-path tools: replacing heavy model inference with sub-5ms gazetteer parsers and pairing vision models with dedicated geometric calculators for building codes. For KTAS, I enforced a native Android client utilizing Zero-Knowledge geofencing, evaluating threat polygons locally on-device. Finally, I demanded empirical validation through synthetic scenario benchmarks rather than trusting model self-evaluations.

This experience proved that LLMs are not autonomous silver bullets. In production, probabilistic models are fragile without deterministic scaffolding. Real impact requires systems architects who constrain model boundaries, enforce local-first privacy, and anchor reasoning within verifiable execution loops.
