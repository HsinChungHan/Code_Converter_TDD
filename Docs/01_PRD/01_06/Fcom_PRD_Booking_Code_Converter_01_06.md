# Booking Code Converter

## Assignment

| Item | Details |
|------|---------|
| **Document Status** | DRAFT 1ST VERSION |
| **Document Owner** | @Dino Yeh |
| **UED** | @Ten Liu |
| **Developers** | BE: @Gary Chen, @Danny Lin |
| | Android: @David Huang |
| | WAP: @Paul Yang |
| | iOS: @Reed Hsin |
| **QA** | TBD |
| **DA** | @Richard Cheng |
| **Figma** | [Code-Converter](https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter?node-id=24353-69) |
| **API Doc** | TBD |
| **Epic Ticket** | [FOOTBALL-9161: Booking Code Converter](https://jira.example.com/browse/FOOTBALL-9161) `BACKLOG` |

---

## Version History

| Date | Memo |
|------|------|
| 2025-01-06 | Added detailed GA Events parameters, API Endpoints, Twitter Tag Bot feature |

---

## Environment

| Platform | Region | Back Office Related |
|----------|--------|---------------------|
| BE | NG, GH | BO Page |
| WAP | | BO Config |
| FE for BO page | | |
| Android | | |
| iOS | | |

---

## Timeline

| System Design | Date |
|---------------|------|
| BE: | |
| Android: | |
| WAP: | |
| iOS: | |

---

## Feature Description

> Allow users to easily convert competitor booking codes or bet slip screenshots into Fcom booking codes and bet directly on Fcom. In a later phase, allow users to generate betting combinations via natural language prompts.

### Phase 1 Scope: Code2Code

**Competitor → Fcom booking code**

1. User inputs a competitor booking code in Fcom app (or via Telegram bot).
2. Backend calls competitor public "load code" APIs, retrieves the bet composition (events, markets, outcomes), maps them to Fcom's offers, and generates an Fcom booking code.
3. The generated Fcom booking code is automatically loaded into Fcom betslip.

### Phase 2 Scope: OCR2Code

**Image → Fcom booking code**

- User shares a bet screenshot (from competitor / social media) to Fcom app or Telegram bot.
- Backend uses OCR + parsing to extract selections, maps them to Fcom offers, generates an Fcom booking code, and loads it into betslip (or replies in TG).

### Phase 3 Scope: Prompt2Code

**Prompt → Fcom booking code**

- User sends a natural language prompt (e.g. "find me 3 games starting today with the highest win probability") via Fcom app widget or Telegram bot.
- Backend uses AI to interpret the prompt, fetches suitable selections from Fcom DB, constructs a booking code, and returns it.

### Platforms

- Android / iOS / WAP
- Telegram bot (existing)
- Shared backend service: **Booking Code Generator**

### Key Value

- Reduce friction for users migrating from other bookies or copying social media bet slips.
- Capture external/social betting traffic into Fcom.
- Provide "smart bet suggestions" (Phase 2) using existing Data + AI.

---

## User Story

| Story Name | As a... | I want to... | So that... |
|------------|---------|--------------|------------|
| **Code2Code** (within Fcom app) | user who sees an interesting bet from another bookie | paste the competitor's booking code into Fcom | I can quickly place the same bet on Fcom without manually rebuilding it |
| **OCR2Code** (Fcom app – share image) | user browsing social media / chat groups | share a bet screenshot directly to Fcom | Fcom can read it, convert it, and let me bet the same combination easily |
| **OCR2Code** (Telegram bot) | user who uses Telegram more than the app | forward a bet screenshot to the Fcom Telegram bot | it can convert it into a Fcom booking code or selections I can reuse |
| **Prompt2Code** (Phase 2) | user who doesn't have a specific code, but has an idea | type a simple request (e.g. "3 safe picks today, highest win probability") | Fcom can generate a booking code for me based on my preferences |
| **Async / long-running flow** | user | be able to leave the screen while the system is converting my image or prompt | I don't feel blocked by long AI/OCR processing times and can continue using the app |

---

## Error Handling

| Error Type | Message |
|------------|---------|
| **Invalid competitor code** | "We couldn't find this booking code on [BookieName]. Please check and try again." |
| **OCR cannot parse image** | "We couldn't recognize a valid bet from this image. Please try another screenshot or a clearer image." |
| **Partial mapping** | "We converted some of the selections, but a few are not available on Fcom." <br> *Show list of missing events/markets if possible.* |
| **Timeouts / internal errors** | "The conversion is taking longer than expected. Please try again later." <br> *Log for monitoring and retry options.* |

---

## Details (SPEC)

### Architecture / Components

#### Frontend

- Fcom app **"Load Code" widget**
- Chat-like interface (for async flow & history)
- OS-level share entry (Android/iOS)
- Telegram bot (existing, reusing same backend)

#### Backend

**Sport Booking Code Generator Service**

**Input types:**
- `type = COMPETITOR_CODE` (raw text code + source bookie)
- `type = IMAGE` (image URL or file reference)
- `type = PROMPT` (free text, later phase)

**Responsibilities:**

1. Parse input (code / image / prompt).
2. Normalize to internal selection structure:
   - event id / name
   - market id / name
   - outcome id / name
   - odds (if needed for mapping / validation)
3. Map external selections to Fcom offers (DB lookup + mapping rules).
4. Build Fcom booking code.
5. Return:
   - booking code
   - normalized selection list
   - error / partial match info if any

#### Competitor API Clients

For each supported competitor:
- `load_code` endpoint config (URL, auth, rate limit, etc.)
- Response mapping to internal schema

#### Mapping Layer

Mapping logic between competitor events/markets/outcomes and Fcom's internal IDs:
- by event date/time + team names + league
- by market type name / code
- by outcome label (e.g. "Home Win", "Over 2.5")

#### AI / OCR Layer

Accepts image and extracts:
- bookmaker name (if possible)
- list of events / teams / markets / odds

Returns a machine-readable structure for the mapping layer.

#### Job / Async Processing

Long-running tasks (OCR / prompt) should be queued:
- Request ID generated
- Status: `PENDING` → `PROCESSING` → `SUCCESS` / `FAILED` / `PARTIAL`
- Frontend can poll or receive push notification / in-app message when done.

---

## Flows

### 1. Code2Code – in-app (text input)

**Inputs:**
- User manually enters competitor booking code into Load Code widget.
- User selects competitor bookie from dropdown (e.g. Bet9ja, BetKing, etc.).

**Flow:**

| Step | Description |
|------|-------------|
| 1 | User opens Load Code widget on home. |
| 2 | User selects Bookie from dropdown. |
| 3 | User inputs booking code text and taps **Load Code**. |
| 4 | App sends request to Booking Code Generator. |
| 5 | Backend calls competitor's `load_code` API, gets selections. |
| 6 | Backend maps those selections to Fcom offers via DB / mapping layer. |
| 7 | Backend generates Fcom booking code (e.g. AF1234) and returns response. |
| 8 | App: <br> • Shows success message: "Converted to Fcom code AF1234" <br> • Automatically opens betslip with selections loaded. |

**Error Scenarios:**

| Scenario | UI Message |
|----------|------------|
| Invalid competitor code / API returns "not found" | "Code not found on [BookieName]. Please check and try again." |
| Partial mapping only (some events not available on Fcom) | "We could only convert 3 out of 5 selections. Missing events: …" |
| Competitor API down / timeout | Monitor @Gary Chen |

**Mockup References:**
1. Home page load code widget
2. Empty mini betslip (a. Refine empty betslip)
3. Code center load code tab

---

### 1.5 Twitter Tag Bot (New Feature)

**Flow:**

| Step | Description |
|------|-------------|
| 1 | User tags Fcom official account on Twitter. |
| 2 | Official account gets notified, finds the post on Twitter by ID. |
| 3 | System converts the booking code. |
| 4 | Reply under the post with the conversion result. |

---

### 2. OCR2Code – in-app (share image)

**Inputs:**
- User taps OS share on a screenshot.
- Chooses Fcom app from share options.

**Flow:**

| Step | Description |
|------|-------------|
| 1 | User sees bet screenshot on social / chat → taps Share. |
| 2 | In system share sheet, user selects Fcom. |
| 3 | Fcom app opens a "Code Converter" chat UI (or dedicated screen) showing: <br> • The shared image <br> • A message "We're converting your screenshot into a booking code…" |
| 4 | App sends request to backend. |
| 5 | Backend pushes job to OCR/AI queue: <br> a. OCR extracts text → events / markets / odds. <br> b. Mapping layer resolves them to Fcom offers. <br> c. Booking code generated. |
| 6 | Once done, backend sends result: <br> • `SUCCESS`: Fcom booking code + selection list <br> • `PARTIAL`: some selections missing <br> • `FAILED`: cannot parse / no matches |
| 7 | App: In chat UI, shows a message: <br> "Here's your converted code: AF1234. Tap to bet." <br> When user taps, open betslip with selections. |

**Notes:**
- User should be able to leave the screen, continue other things.
- When result is ready: Notification / in-app message
- Chat history retains input image + output code

---

### 3. OCR2Code – Telegram bot

**Flow:**

| Step | Description |
|------|-------------|
| 1 | User forwards or uploads a bet screenshot to Fcom TG Bot. |
| 2 | Bot receives image and sends to backend. |
| 3 | Backend runs same OCR + mapping + booking code generator. |
| 4 | Bot replies in chat: <br> **On success:** "Converted booking code: AF1234" (Optionally list selections) <br> **On partial/failed:** explain what went wrong. |

---

### 4. Prompt2Code – app widget or Telegram (Phase 2)

**Flow:**

| Step | Description |
|------|-------------|
| 1 | User opens Code Converter chat (app) or TG Bot and types a prompt, e.g.: <br> "Find 3 matches starting today with the highest win probability." |
| 2 | Client sends request. |
| 3 | Backend: <br> a. Uses AI model to parse intent & constraints (number of events: 3, date: today, criteria: highest win probability) <br> b. Queries Fcom DB / recommendation engine for suitable selections. <br> c. Constructs booking code. |
| 4 | Returns result → booking code + explanation. |
| 5 | UI shows: "Here is a code based on your request: AF5678" <br> List events & markets. |

---

## Use Case

### Supported Bookies

| Rank | Bookies | Country | Author |
|------|---------|---------|--------|
| 1 | Sporty | NG, GH | |
| 2 | MSport | NG/GH/UG/ZM | @Danny Lin |
| 3 | Bet9Ja | NG | @Gary Chen |
| 4 | Bangbet | KE, UG, NG, GH, TZ | @Danny Lin |
| 5 | BetKing | NG | @Gary Chen |
| 6 | 1xBet | Global | |
| 7 | Betway | Global | |
| 8 | LiveScore Bet | UK | |
| 9 | Stack | Global | |
| 10 | BetPawa | Africa | |
| 11 | Bet365 | Global | |

### Use Case Scenarios

1. **In-app text code conversion**
   - User sees a booking code on a competitor site.
   - Opens Fcom app → Load Code widget → selects competitor → inputs code → taps Load → Fcom converts and loads betslip.

2. **In-app image share conversion**
   - User sees a bet screenshot on Instagram / WhatsApp.
   - Taps Share → selects Fcom → app opens chat view and uploads image → system converts → returns Fcom booking code → user taps to bet.

3. **Telegram screenshot conversion**
   - User forwards a bet screenshot to Fcom TG bot.
   - Bot replies with Fcom booking code and selection list.

4. **Prompt-based booking code (Phase 2)**
   - User opens Code Converter chat in Fcom app.
   - Types: "3 matches today, highest win probability, total odds around 3.0."
   - System returns a booking code built from DB with matching criteria.

---

## API Endpoints

| Page | API Endpoint | Memo |
|------|--------------|------|
| Home Page | `POST /orders/converter/code` (New) | Convert Code2Code |
| Home Page | `GET /orders/converter/config/providerCountries` (New) | Get provider country config |
| Home Page | `GET /orders/share/:shareCode` | Get order record by share code |

---

## BO Page Design

*TBD*

---

## Copywriting

*TBD*

---

## GA Events

### Event Definitions

| Event Name | Trigger | Parameters |
|------------|---------|------------|
| `code_converter__open_bookie_spinner` | Open bookie selector | `location`: widget / empty_betslip / code_center |
| `code_converter__choose_bookies` | Click submit CTA | `bookie`, `country`, `location` |
| `code_converter__load_code` | Click Load Code CTA | `bookie`, `country`, `location` |
| `code_converter__load_code_successfully` | Get successful response from API | `bookie`, `country`, `location` |

### Parameter Values

**location possible values:**
- `widget` - Home Widget
- `empty_betslip` - Empty Betslip
- `code_center` - Code Center Tab

---

## Follow-up

| Task | Owner | Status | Action Items |
|------|-------|--------|--------------|
| Code2Code BE | @Gary Chen, @Danny Lin | IN PROGRESS | • Integrate bookies<br>• Mapping events/markets & outcomes<br>• Complete code conversion mechanism |
| Code2Code Client tech | | | Load code component expand |

---

## Metrics

### North Star Metric (Phase 1): Converter-attributed Betslip Loads

**Definition:**
The number of sessions/users who successfully convert a competitor code and load the resulting selections into the betslip.

**Inclusion criteria (attribution):**
- The conversion result is **Success** (or **Partial**, if Phase 1 counts partial loads as valid) and the betslip is loaded.
- The betslip load event must carry:
  - `source = "code_converter"`
  - a unique `conversion_request_id` (or equivalent job/request identifier) to ensure end-to-end traceability.

**Notes:**
- This metric focuses on the Phase 1 core value: reducing friction by turning external codes into an actionable betslip on Fcom.
- It does not require a bet placement after the betslip is loaded.

---

## DA Requirements

### Monitor Engagement

**3 entrances (widget / empty betslip / code center load code tab)**

Observe funnels:
1. Bookies spinner
2. Select bookies
3. Input booking code
4. Load code

### Conversion Success Rate

1. Track conversion volume and conversion success rate by bookie, calculated separately
   - Conversion success rate should explicitly include and track partial results
2. The goal is to identify the most popular third-party bookies and to improve the conversion success rate for those bookies
3. Compare the proportion of Fcom / Sporty codes versus other bookies' codes

### BE Tables

Converted booking codes data:
- Bookie
- Number of total selections
- Number of successful selections
- *TBD: how will the failed selections be stored in the database? What info do we have about the failed selections?*

---

## Design Assets & Inspiration

### Home – Load Code Widget (existing)

**Case 1 (text input):**
- Bookie dropdown (required for competitor mapping)
- Text field for code
- "Load code" CTA

**Case 3 (prompt) (Phase 2):**
- Additional mode / toggle: "Ask AI to build a code"
- Opens chat view or expands into prompt input.

### Chat-style Interface (recommended for OCR & Prompt)

**Pros:**
- Handles slow AI / OCR naturally (async).
- Clear history: user can see previous images/requests & results.
- Easy to extend to future features (e.g. explanations / tips).

### Notifications

If processing takes > X seconds, show:
> "We're still working on it, you can continue using the app. We'll notify you when it's ready."

---

## Others

### Designs of Other Products

*Reference designs from competitors for inspiration.*

