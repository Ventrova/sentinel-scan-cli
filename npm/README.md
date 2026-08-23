# sentinel-scan-cli (npm)

Free, zero-dependency 15-attack prompt-injection / jailbreak smoke test for
your own LLM endpoint, mapped to the [OWASP Top 10 for LLM Applications
(2025)](https://genai.owasp.org/llm-top-10/). This is the JS/Node port of
the [Python original](https://github.com/Ventrova/sentinel-scan-cli) - same
attack corpus, same OWASP mapping, same JSON output shape.

Requires Node 18+ (uses the built-in `fetch`, no dependencies).

```bash
npx sentinel-scan-cli --demo
```

`--demo` runs a built-in vulnerable target, no network calls, no API key.
See the exact output first: **https://ventrova.dev/sample-report**

```bash
# Run it against your own OpenAI-compatible endpoint
npx sentinel-scan-cli \
  --url https://api.openai.com/v1/chat/completions \
  --api-key $OPENAI_API_KEY \
  --model gpt-4o-mini \
  --system-prompt-file my_system_prompt.txt \
  --secret "some-marker-string-if-you-have-one-planted"
```

Full docs, the attack list, flags, and OWASP category mapping:
**https://github.com/Ventrova/sentinel-scan-cli**

Want an LLM-judged audit with a written report instead of a heuristic scan?
**https://ventrova.dev/audit**

MIT licensed. Built by [Ventrova](https://ventrova.dev).
