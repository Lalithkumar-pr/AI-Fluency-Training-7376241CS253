# Day 5 Assessment: Serving Models Your Way

## Scenario overview
This project uses the same base model, Qwen 2.5 1.5B, for three distinct assistants: a cautious cybersecurity incident explainer, a practical photography mentor, and a placement aptitude tutor that distinguishes hints from worked solutions. Different system instructions and parameter defaults demonstrate how a model can be configured for different tasks without training three new models.

## Concepts

### Ollama and request flow
Ollama is a local model runner and serving system. Its CLI lets a user pull, create, inspect, run, and stop models; its background server accepts HTTP requests; and its runtime loads model data and performs inference. Model files are stored in Ollama's local model storage, whose path depends on the operating system and configuration. A request reaches the server, which identifies and loads the requested model if needed, prepares the prompt, invokes inference, and returns generated text. Streaming returns chunks as generation proceeds.

### Modelfiles and custom models
A Modelfile configures a model from an existing base. `FROM` selects `qwen2.5:1.5b`; `PARAMETER temperature` controls randomness, `num_ctx` sets context capacity, and `repeat_penalty` discourages repetition. `SYSTEM` defines the default role and behavior. The cyber assistant uses cautious language, the photography mentor uses practical coaching, and the aptitude tutor gives hints before solutions. Creating these custom names does not train new weights or download three full copies; they are configurations built on the existing model.

### Prompt precedence
The Modelfile system prompt is a default. A system message supplied by the calling program can override that default for the request. This is useful in agent frameworks because the application needs to adapt instructions to a particular task or user rather than being permanently constrained by one model-level persona.

### API endpoints and compatibility
`/api/generate` accepts a prompt-oriented request. `/api/chat` accepts role-tagged messages and suits conversational applications. Ollama's OpenAI-compatible endpoint, such as `/v1/chat/completions`, accepts a familiar chat-completion request shape. This can reduce migration work: a client may need only a different base URL and model name, though provider-specific features can differ.

### Streaming and latency
Streaming delivers output chunks before the complete answer is ready. TTFT (time to first token) measures the wait until the first generated content arrives; total time measures the full request duration. Streaming improves perceived responsiveness because users see output sooner, but does not necessarily reduce total computation time. The script records local timings, which vary by hardware, model load state, and prompt.

### Context and memory
`num_ctx` controls the context window. Longer active sequences generally require more KV-cache memory because key/value states are retained for tokens. `OLLAMA_KEEP_ALIVE` controls how long a model stays loaded after use. `OLLAMA_NUM_PARALLEL` controls parallel request processing; more concurrent sequences can increase KV-cache demand. Exact memory use depends on architecture, precision, context, and concurrency.

### PagedAttention and prefix caching
Naive cache allocation can waste memory when requests have different sequence lengths. PagedAttention stores KV-cache data in fixed-size blocks and uses a block table to map logical token positions to physical blocks, reducing fragmentation and enabling flexible allocation. Prefix caching can reuse computed states for an identical shared prompt prefix. This can help agents that resend the same system prompt, when the serving engine supports caching and the prefix matches.

### Batching and metrics
Static batching groups requests together, potentially making short requests wait for longer ones. Continuous batching admits new requests as others finish, improving accelerator utilization. Throughput measures completed work per unit time. TTFT measures initial response delay; TPOT is the average time per output token after generation starts; P95 latency is the latency below which 95% of requests finish. Higher utilization and larger batches can improve aggregate throughput but may increase queueing or per-request latency. The right balance depends on workload and service targets.

## Ollama vs vLLM

| Basis | Ollama | vLLM |
|---|---|---|
| Built for | Local development and convenient small deployments | High-throughput concurrent serving |
| Hardware | Supported CPU/GPU systems; small models can run on ordinary machines | Usually benefits from capable accelerators and sufficient GPU memory |
| Concurrent requests | Supports parallelism with configuration and resource limits | Continuous batching schedules concurrent sequences |
| Memory | Runtime manages model and cache; concurrency/context affect demand | PagedAttention manages KV cache in blocks |
| Setup/model format | Simple CLI, Modelfiles, local HTTP API | More serving configuration; supports compatible model checkpoints and API serving |
| Choice for one user | Ollama: simpler local setup for these assistants | May be unnecessary overhead for personal use |
| Choice for 100 simultaneous users | Measure capacity; a single instance may be constrained | Evaluate vLLM for batching and cache efficiency; load testing is still necessary |

## Implementation
The repository contains three Modelfiles and `api_demo.py`. The script sends non-streaming and streaming `/api/chat` requests, reports elapsed time, TTFT and token rate when the server supplies token counts, and demonstrates a request-level system prompt override. Create the custom models using the commands in `README.md`, then run the script.

## Observations — fill after running
Do not present sample or invented measurements as actual results. Run at least three prompts per scenario, repeat one prompt, and check `ollama ps` or `/api/ps` to determine whether the model remains loaded.

| Scenario / prompt | Followed default behavior? | Override result | TTFT | Total time | Tokens/s | Repeat/load observation |
|---|---|---|---|---|---|---|
| Cyber: unfamiliar login | [record] | [record] | [record] | [record] | [record] | [record] |
| Cyber: suspicious email | [record] | — | [record] | [record] | [record] | [record] |
| Cyber: failed logins | [record] | — | [record] | [record] | [record] | [record] |
| Photo: star settings | [record] | [record] | [record] | [record] | [record] | [record] |
| Photo: motion blur | [record] | — | [record] | [record] | [record] | [record] |
| Photo: portrait exposure | [record] | — | [record] | [record] | [record] | [record] |
| Aptitude: train crossing | [record] | [record] | [record] | [record] | [record] | [record] |
| Aptitude: hint request | [record] | — | [record] | [record] | [record] | [record] |
| Aptitude: practice question | [record] | — | [record] | [record] | [record] | [record] |

Add your own paragraph below the table describing instruction-following, surprises, first-versus-repeat timing, and whether the model was loaded. Include screenshots of `ollama list`, `ollama show` for each model, `ollama ps`, and script output.

## Suitability and conclusion
Ollama is suitable for one person testing these assistants because it offers simple local model management, Modelfiles for reusable defaults, and HTTP APIs for scripts. An OpenAI-compatible endpoint can make client migration easier. A deployment serving many simultaneous users must also manage GPU memory, scheduling, queueing, and latency. vLLM's PagedAttention and continuous batching target these concurrency challenges, but the choice should be validated against measured traffic, hardware, throughput, and latency requirements. Ollama is a practical local development choice; a server such as vLLM becomes worth evaluating when concurrent serving and resource utilization become central.
