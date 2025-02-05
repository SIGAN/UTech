# Continue.Dev

Update Config.json and keep only one model
```json
    {
      "model": "claude-3-5-haiku-latest",
      "provider": "anthropic",
      "apiKey": "<INSERT SHARED API KEY HERE>",
      "title": "Claude 3.5 Haiku"
      "provider": "anthropic",
    }
```

Leave autocomplete as-is, or just use Claude 3.5 Haiku

```json
  "tabAutocompleteModel": {
    "title": "Tab Autocomplete",
    "model": "claude-3-5-haiku-latest",
    "provider": "anthropic",
    "apiKey": "<INSERT SHARED API KEY HERE>"
  }
```

Note, continue.dev allows use of tools!

Moreover, Continue.dev recommends to run `Qwen2.5-Coder 1.5B` with Ollama locally for autocomplete.

This will use Q4_K_M quantized model, which is approximately 986MB. If your hardware allows use 3B version.

```json
  "tabAutocompleteModel": {
    "title": "Qwen2.5-Coder 1.5B",
    "provider": "ollama",
    "model": "qwen2.5-coder:1.5b-base"
  },
```

# aider

There is no configuration required, just run it with parameters.

```bash
cd /workspace/eve
aider --model sonnet --api-key anthropic=<INSERT SHARED API KEY HERE>
```

Another option is to set environment variables:

```bash
export ANTHROPIC_API_KEY=<key> # Mac/Linux
setx   ANTHROPIC_API_KEY <key> # Windows, restart shell after setx
```
