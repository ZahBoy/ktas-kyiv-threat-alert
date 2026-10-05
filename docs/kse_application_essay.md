# KSE Agentic AI School Application Essay

**Prompt:** *"Додай есе до 250 слів англійською мовою (що ти робив, де модель помилилась, як ти змінив підхід і що забрав із цього досвіду)"*  
**Word Count:** 228 words (Limit: strictly under 250 words)

---

### Essay Text

When designing AI systems for wartime Ukraine, I tackled two life-safety challenges: an automated blueprint auditor checking architectural accessibility for wounded veterans, and the Kyiv Threat Alert System (KTAS) to mitigate alert fatigue.

Basic prompting failed almost immediately. On the accessibility project, language models produced promotional fluff and hallucinated spatial dimensions, misjudging ramp inclines and wheelchair turning radii. For KTAS, conversational models proposed a standard Telegram bot, ignoring Telegram's 30 message-per-second broadcast ceiling, Android Doze mode, and the inability of bots to override nighttime Do Not Disturb. Worse, the suggested architecture centralized user GPS coordinates on a server, creating a dangerous wartime surveillance risk.

I shifted from open-ended chat to agentic systems engineering. Using structured brainstorming and humanizer constraints, I stripped away AI clichés and isolated the core engineering requirements. I then routed critical logic away from raw inference into deterministic tools: sub-5ms gazetteer parsers for district recognition and dedicated geometric calculators for building codes. For KTAS, I implemented a native Android client with Zero-Knowledge geofencing, evaluating threat polygons directly on-device to ensure privacy. Finally, I replaced model self-evaluations with empirical synthetic scenario benchmarks.

This experience proved that language models are not autonomous silver bullets. In production, probabilistic reasoning breaks without deterministic scaffolding. Real impact demands architects who enforce strict tool boundaries, protect user privacy on-device, and ground AI within verifiable execution loops.
