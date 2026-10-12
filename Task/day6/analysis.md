# Day 6 Task Analysis — Reliable Tool Calling

**Scenario: Campus Event Planner**

## 1. Scenario and design

I built a campus event planner rather than reusing the course-fee scenario from the lab manual. It has two tools: `get_venue_capacity` looks up a venue category's capacity, and `estimate_refreshment_cost` estimates the total cost of one refreshment package per attendee. The small fixed data set makes results reproducible and keeps the focus on reliable tool calling rather than data collection.

The venue categories are `lecture_hall`, `seminar_room`, and `computer_lab`. Their capacities are 180, 45, and 60 respectively. The refreshment packages are `water_snack` at ₹35 per attendee, `tea_snack` at ₹55, and `lunch_box` at ₹120. These are example values for this task, not official college prices or confirmed venue capacities.

## 2. Chat Completions request and response

Chat Completions sends a request containing a `model`, a `messages` list, and optional settings such as `temperature`, `max_tokens`, `stream`, `tools`, `tool_choice`, and `response_format`. The messages preserve the conversation and use roles such as `system`, `user`, `assistant`, and `tool`. In this project, the system message explains the planner's responsibilities and the request includes both tool schemas.

The response contains `choices`; each choice has a message and a `finish_reason`. `stop` means generation completed normally, so the agent can use the final text if there are no tool calls. `tool_calls` means the assistant is requesting one or more tool executions; the program must run them and return their results. `length` means generation hit the token limit and may have produced incomplete text or arguments, so the agent retries with a larger limit instead of treating the partial reply as complete. `message.content` may be empty when a tool call is represented in `message.tool_calls`; code that only reads `content` can miss the requested action.

## 3. OpenAI-compatible endpoints

An OpenAI-compatible endpoint accepts the common client request and response format. The OpenAI Python package acts as an HTTP client; the `base_url` determines where the request goes. This project can point to Groq or an Ollama local endpoint through `config.py`, without rewriting the agent loop. In this setup, changing provider settings and the model name is enough for the supported Chat Completions path.

Compatibility does not promise that every feature is implemented identically. In particular, strict JSON-schema structured outputs, tool-call reliability, seeds, and other optional parameters can vary by provider and model. A provider error during schema mode is an observation to record, not proof that the Python extraction code is wrong.

## 4. Streaming and the Responses API style

Streaming returns a sequence of chunks, each carrying a delta such as a new piece of text. It improves time to first token, so a person can start reading before the full answer is ready. It does not necessarily reduce the total generation time. In an agent loop, the program usually needs the complete tool name and complete arguments before it can validate and execute them. Streaming tool arguments arrive in fragments that must be assembled correctly, so this minimal task leaves streaming off.

The Responses API style uses an `input` field and typed output items, and can support server-managed state through a previous response identifier where offered. Chat Completions uses a `messages` list and returns `choices[0].message`. This course task stays with Chat Completions because it is broadly implemented by the selected OpenAI-compatible endpoints and makes the agent's history management explicit in Python.

## 5. Five steps of a tool call

1. The client sends system/user messages together with the JSON Schema tool definitions.
2. The model responds with `finish_reason = tool_calls` and one or more requested calls, each with an ID, function name, and argument text.
3. The Python program parses the argument text as JSON, checks that the tool exists, validates the arguments, and executes the registered function only after validation.
4. The program appends one `role: tool` message per call, with the matching `tool_call_id` and the result or a readable error.
5. The conversation is sent back to the model, which can explain the result or correct a malformed request.

The model does not execute Python functions. Our code does. This matters because the arguments are generated text and may be invalid, misleading, incomplete, or outside the tool's contract. The code must treat them as untrusted input.

## 6. Tool schema and selection

The tool schemas use `description` to explain each tool's purpose, `properties` to define the allowed arguments, `enum` to limit categories to a fixed set, `required` to identify mandatory arguments, and `additionalProperties: false` to reject extra keys. The same `SCHEMAS` dictionary is used to send schemas to the model and validate the received arguments, reducing the chance that the model-facing contract and the program's checks drift apart. `strict: true` can be requested by some providers, but support is not universal; the local validator remains necessary.

`tool_choice: auto` lets the model decide whether a tool is needed; it fits the event planner because greetings need no tool while capacity and cost questions do. `none` prevents tool calls, `required` forces some tool call, and a named function forces one particular tool. `parallel_tool_calls: false` can be useful while debugging, but parallel calls should still be handled correctly when the provider returns them.

## 7. Structured outputs compared with tools

Tool calling asks the model to request an action such as looking up venue capacity or estimating refreshment cost. Python executes that action and sends back a result. Structured outputs ask the model to return data in a defined format, such as extracting `event_type`, `attendees`, and `needs_refreshments` from an event description. JSON mode aims to produce valid JSON but does not force the exact field structure. Schema mode asks for the specified fields and types, where supported.

A well-shaped JSON object can still be factually wrong: for example, it could return 120 attendees when the request says 1200. A schema controls form, not truth. Use a tool when the system must retrieve a value or perform a calculation using known data; use structured output when application code needs fields extracted or classified from text.

| Basis for comparison | Tool calling | Structured outputs |
|---|---|---|
| What the model is asked to do | Request an operation using a named function and arguments | Return data in a defined format |
| Who performs the action or produces final data | Python executes the requested tool; model then explains result | Model produces the structured fields |
| How result shape is controlled | Function JSON Schema plus local validation | JSON mode or JSON Schema response format |
| What can still go wrong | Invalid arguments, unknown tool, wrong values, tool errors, loops | Correct JSON shape can contain incorrect or incomplete facts |
| How code guards against it | Parse, registry lookup, schema validation, error feedback, retry and limits | Parse JSON, check required fields/types and verify factual values where possible |
| Support across servers/models | Tool calling is common, but reliability varies | JSON mode is common; strict schema support varies |
| Choice for fetching/calculating something | Tool calling, because code executes a controlled lookup/calculation | Not the first choice; structured output does not execute a lookup |
| Choice for extracting fields from a sentence | Possible, but unnecessary if no action is needed | Structured output, because downstream code needs a predictable object |

## 8. Failure handling and repair pattern

The agent uses four stages. First, `json.loads` parses the generated argument string inside a `try` block. Second, the tool registry is checked with `.get()` so an unknown function name returns a message rather than raising a `KeyError`. Third, `validate_arguments` checks that arguments are an object, required fields are present, extra fields are absent, types match, and enum values are allowed. Fourth, the function executes inside a `try` block. Each failure is returned as a string so it can be included in a tool message and read by the model on the next turn.

The repair pattern is to treat validation failures as observations for the model instead of crashing. For example, a missing `venue_type` message tells the model which argument is required. Invalid JSON is reported as a parse problem. Unknown tools list the available tools. Wrong types, invalid enum values, and extra arguments describe the expected contract. The model may then correct its call, though recovery is not guaranteed.

A truncated response is different: the output limit may have cut off otherwise reasonable generation, so the agent increases `max_tokens` and retries. A malformed but complete tool call is instead returned as feedback, giving the model a chance to repair its arguments. Repeated identical calls are counted; after three occurrences the agent stops. The loop also has a maximum-step limit.

## 9. Parallel tool calls

A model can request more than one tool in a single assistant turn. The event-planning question asking for both computer-lab capacity and lunch-box cost is designed to make two independent lookups possible. The agent loops over every item in `message.tool_calls`, preserves the assistant tool-call turn, and appends one tool message for every call with its own matching `tool_call_id`. If an ID is left unanswered, a subsequent API request may be rejected or the conversation may be invalid. Whether the selected model actually returns parallel calls must be confirmed in the run log; the question alone does not prove that it did.

## 10. Fault injection and observations

Fault injection supplies deliberately malformed calls directly to the handler. It requires neither a model nor internet because the handler and tool functions run locally. This makes the tests deterministic and repeatable. It demonstrates that many agent reliability bugs live at the boundary between generated arguments and ordinary application code, not just in model reasoning.

The included test set covers valid arguments, invalid JSON, an unknown tool, missing required arguments, a wrong type, an enum value outside the allowed list, an invented argument, a case-mismatched tool name, a JSON array instead of an object, an empty argument string, and an extra field. The fault script prints the actual response for each case. It is important not to claim that a real provider produced these faults: they are injected by the test harness.

### Fault table

Run `python inject_faults.py` and copy the exact returned message from your terminal into this table. “Run continued” means the fault test loop printed the next case without crashing.

| Injected fault | Message returned | Did the run continue? |
|---|---|---|
| Invalid JSON | Fill from local run | Y/N after run |
| Unknown tool | Fill from local run | Y/N after run |
| Missing required | Fill from local run | Y/N after run |
| Wrong type | Fill from local run | Y/N after run |
| Value outside enum | Fill from local run | Y/N after run |
| Invented argument | Fill from local run | Y/N after run |
| User-designed fault 1: case-mismatched tool | Fill from local run | Y/N after run |
| User-designed fault 2: JSON array arguments | Fill from local run | Y/N after run |
| Empty argument string | Fill from local run | Y/N after run |

### Agent behaviour table

Run `python robust_agent.py`. Record what your selected provider/model actually did; results can vary.

| Question | Steps | Tool calls made | Final answer | Parallel calls? | `finish_reason=length`? |
|---|---:|---|---|---|---|
| Capacity of a computer lab | Fill after run | Fill after run | Fill after run | Y/N | Y/N |
| Tea/snack cost for 80 attendees | Fill after run | Fill after run | Fill after run | Y/N | Y/N |
| Computer-lab capacity and lunch-box cost for 50 people | Fill after run | Fill after run | Fill after run | Y/N | Y/N |
| Capacity of a stadium (invalid value temptation) | Fill after run | Fill after run | Fill after run | Y/N | Y/N |
| One-line event welcome message | Fill after run | Fill after run | Fill after run | Y/N | Y/N |

### Before and after guards

The guarded version reports invalid input as a tool result, giving the model an opportunity to recover. Compare this with your Day 3 implementation or a local copy with guards disabled. Record actual step counts and whether it loops. Do not invent a result if you have not run the comparison.

| Behaviour on the invalid venue question | Unguarded/Day 3 agent | Guarded Day 6 agent |
|---|---|---|
| Steps used | Fill after run | Fill after run |
| Final answer | Fill after run | Fill after run |
| Did it loop? | Y/N | Y/N |

### Structured outputs table

Run `python structured_demo.py` and record the result from your provider. The script prints the raw response and attempts to parse it. A provider may reject schema mode; record the error exactly.

| Case | Actual provider result | Classification |
|---|---|---|
| No output constraint | Fill after run | Prose / valid JSON / other |
| JSON mode | Fill after run | Valid JSON / invalid JSON / error |
| Schema mode | Fill after run | Correct schema / wrong shape / error |

## 11. Suitability and conclusion

The most important guard in this implementation is validation before function execution, together with returning actionable error messages. A schema can prevent missing fields, unexpected fields, type mismatches, and values outside enumerated categories when those checks are enforced. It cannot establish that the user's request is true, guarantee that a model chooses the right tool, or guarantee that a correctly typed value is semantically sensible. The tool itself should also validate domain-specific constraints, such as a non-negative attendee count.

Fault injection is valuable because it deliberately tests failure paths every time, rather than waiting for a probabilistic model to make a particular mistake. The model-backed observations must be completed from the actual provider run: which faults occurred naturally, whether calls were parallel, whether truncation happened, and which structured-output modes worked. Tool calling is the right choice for the planner's lookups and calculations because Python owns the data and calculation. Structured outputs are appropriate for extracting event details into a predictable object that another program can process.
