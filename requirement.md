
# Outlook Email Automation Desktop Tool — Requirements (Final)

**Owner:** Rahul  
**Date:** 25 Aug 2025 (IST)  
**Stack:** Python Desktop (PyQt6), SQLite, Microsoft Graph API, Zoom API

---

## 1) Problem & Goals
- **Problem:** Outlook coordination (compose, reminders, Zoom links, RSVP, attachments) is repetitive and time-consuming.
- **Goal:** Shrink common multi-step flows into **minimal-input editable drafts** using a **Template Library** and **Quick Actions**.

**Objectives**
- Template-based drafts always open for review (never auto-send).
- Non-AI, rules/logic only.
- Optional Zoom integration for meeting creation and sharing.

---

## 2) Personas
- **Analyst/IC:** needs fast Zoom invites and nudges.
- **Project Manager:** tracks RSVPs and non-responders.
- **Ops/Admin:** applies rules, files messages, and manages attachments.

---

## 3) Feature Set (Finalized)
### Core (Must-Have)
1. **Send Mail (Editable Templates)** — Multi-recipient, signature injection, Zoom link insertion.  
2. **Send Reminders** — From selected sent mail; bulk to non-responders.  
3. **Response Tracking** — Per-recipient status via `internetMessageId`/`conversationId`.  
4. **Attachment Downloading** — Manual and rule-based; rename, zip, save to local/OneDrive/SharePoint.  
5. **Template Library** — CRUD, categories (Meetings/Follow-ups/General/Attachments), placeholder resolution.  
6. **Quick Actions** — Zoom Invite / Follow-up / Thank You / Notes / Forward with FYI.

### Important (Should-Have)
7. **RSVP Tracker** — Accepted/Tentative/Declined/None, nudge “None”.  
8. **Send & File** — Move sent mail to target folder by rule.  
9. **Snooze / Follow-up Flag** — Re-surface at time X.  
10. **Convert to PDF** — Archive selected email as PDF.  
11. **Signature Switcher** — Per-template selection/import.

### Optional (Nice-to-Have)
12. **Share Last Zoom Recording** — Insert latest recording link.  
13. **Export to CSV** — Recipients from a thread.

---

## 4) UI / UX
- **Main Layout:** Left navigation (Templates, Quick Actions, Reminders, Attachments, RSVP, Settings); Right content panel.
- **Template Editor:** Name, Category, Subject, Body (HTML/plain), Placeholder manager, Signature chooser, Live preview, Export JSON.
- **Dashboards:** Reply status per recipient; RSVP status per event; Rules manager for attachments.

**Diagrams (SVG):**  
- UI Flow: [ui_flow.svg](ui_flow.svg)  
- Main UI Mockup: [ui_mockup_layout.svg](ui_mockup_layout.svg)  
- Architecture: [architecture.svg](architecture.svg)

**ASCII Flow**
```
Login → Dashboard
  ├─ Templates (List+Editor) ─→ Draft
  ├─ Quick Actions ───────────→ Draft
  ├─ Reminders ───────────────→ Draft
  ├─ Attachments (Rules+Save)
  ├─ RSVP Tracker ────────────→ Draft
  └─ Settings
```

---

## 5) Template Library (Schema & Examples)
**Schema (JSON)**
```json
{
  "name": "Zoom Meeting Invite",
  "category": "Meetings",
  "subject": "Zoom Meeting with <RecipientFirstOrOrg> — <ShortTopic>",
  "body": [
    "Hi <RecipientName>,",
    "Please join the Zoom call at <ZoomLink> on <LocalDateTime>.",
    "<UserMessage>",
    "Regards,",
    "<Signature>"
  ],
  "placeholders": {
    "ShortTopic": {"type": "string", "required": false},
    "LocalDateTime": {"type": "datetime", "required": false},
    "ZoomLink": {"type": "url", "required": true},
    "UserMessage": {"type": "multiline", "required": false},
    "Signature": {"type": "signature", "required": false}
  },
  "defaults": {"ShortTopic": "Catch‑up"},
  "useSignature": true
}
```

**Starter Templates**
- **Zoom Meeting Invite**
- **Follow-up Reminder**
- **Thank You Note**
- **Forward with FYI**
- **Share Meeting Notes**

(Full JSON examples are already included in the canvas and can be exported within the app.)

**Placeholder Resolution Order:** Template defaults → user/org defaults → runtime inputs → computed values (ZoomLink/LocalDateTime).

---

## 6) Integrations

### 6.1 Microsoft Graph (Delegated OAuth, Desktop Public Client)
**Scopes:** `Mail.ReadWrite`, `Mail.Send`, `MailboxSettings.Read`, `Calendars.ReadWrite`, `offline_access`, (`Files.ReadWrite`, `Sites.ReadWrite.All` optional).  

**Key Endpoints (v1.0):**
- Create Draft: `POST /me/messages`  → Send: `POST /me/messages/{id}/send`
- Quick Send: `POST /me/sendMail`
- Messages: `GET /me/messages`, `PATCH /me/messages/{id}`, folder moves
- Attachments: `GET /me/messages/{id}/attachments`
- Delta: `GET /me/mailFolders/{id}/messages/delta`
- Calendar: `POST /me/events`, `GET /me/events/{id}` (attendees `responseStatus`)
- Webhooks: `POST /subscriptions` (messages/events)

**Reply Detection:** match `In-Reply-To` / `References` with original `internetMessageId` or use `conversationId` grouping.

### 6.2 Zoom API (Optional)
- Auth: Zoom OAuth per user. Scopes: `meeting:write`, `recording:read`.
- Flows: Create meeting → `join_url`; optionally list latest recording for share.

---

## 7) Architecture
- **Desktop UI:** PyQt6 dialogs/grids.  
- **Service Layer:** httpx/asyncio for Graph/Zoom; rules engine; template resolver.  
- **Local DB:** SQLite (SQLAlchemy); WAL mode.  
- **Background Worker:** thread/async tasks for delta sync and rules.  
- **Webhook Receiver:** local FastAPI (optional), or polling fallback.

---

## 8) Data Model (SQLite)
- **Users**(id, displayName, email, timeZone, preferencesJSON)  
- **Templates**(id, ownerUserId, name, category, schemaJSON, version, isDefault)  
- **Signatures**(id, ownerUserId, name, html, isDefault)  
- **Messages**(id, graphMessageId, internetMessageId, conversationId, subject, sentAt, metadataJSON)  
- **Recipients**(id, messageId, email, name, status [Pending|Replied|Bounced], lastChange)  
- **Rules**(id, ownerUserId, type, criteriaJSON, actionsJSON, enabled)  
- **Jobs**(id, type, schedule, status, lastRun, resultJSON)  
- **Integrations**(id, userId, provider [Zoom], tokensJSON)

---

## 9) Scheduler, Webhooks & Sync
- Subscribe to `messages` and `events`; store delta tokens.  
- Backoff strategy using Graph throttling headers.  
- Idempotent processing via last processed IDs.  
- Polling fallback when webhooks unavailable.

---

## 10) Security & Compliance
- MSAL for tokens; encrypt at rest (OS keyring / Fernet).  
- Least privilege; tenant admin consent for advanced scopes.  
- PII minimization; redact logs; user-initiated purge.  
- Audit actions (who/when/template).

---

## 11) Error Handling & Resilience
- User-friendly surface with remediation hints.  
- Retries with exponential backoff; handle HTTP 429/5xx.  
- Graceful Zoom failures (generate draft without link + warning).  
- Dead-letter for failed jobs; retry UI.

---

## 12) Performance & Limits
- Draft generation target: < 2s (no Zoom), < 3s (with Zoom).  
- Use `/$batch` for recipient status checks; paginate queries.  
- Cache folders/signatures locally.

---

## 13) Testing Strategy
- Unit tests: template resolver, rules engine, RSVP parser.  
- Integration: Microsoft Graph sandbox/test tenant; Zoom sandbox.  
- Contract tests: webhook payloads & delta tokens.  
- UI tests: PyQt6 interactions; accessibility.

---

## 14) Deployment & Ops
- Packaging: PyInstaller/Briefcase; code-signing recommended.  
- Config: `settings.json` per user/tenant.  
- Observability: structured logs; metrics (draft latency, reminders).  
- Feature flags: enable/disable Zoom/RSVP/rules.

---

## 15) Analytics (Privacy-Respectful)
- Local counters (template usage, reminders).  
- Error categories & success rates.  
- Optional anonymous telemetry toggle.

---

## 16) Milestones / Rollout
**MVP:** Auth, Template Library CRUD, Quick Actions (Zoom Invite/Follow-up/Thank-You), Response Tracking (basic), Manual attachment save.  
**Phase 2:** RSVP tracker, Rules engine, Send & File, Snooze/Flags.  
**Phase 3:** Recording share, Convert to PDF, Export CSV, Webhooks optimization, Admin console.

---

## 17) Acceptance Criteria (MVP)
- Drafts created from templates with correct placeholder resolution.  
- Zoom Invite draft produced with valid `join_url` (if Zoom connected).  
- Response tracking accurate for ≥90% within 5 minutes.  
- Attachment save applies rename pattern.  
- No auto-send without explicit user action.

---

## 18) Risks & Mitigations
- **Graph throttling:** batching + backoff.  
- **Token expiry/corruption:** MSAL refresh + reauth flow.  
- **Signature rendering variances:** test desktop/OWA.  
- **SQLite locking:** WAL mode; short transactions.  
- **Cross-platform packaging:** test on Windows/macOS/Linux.

---

## 19) Example Templates (JSON)
```json
[
  {
    "name": "Zoom Meeting Invite",
    "category": "Meetings",
    "subject": "Zoom Meeting with <RecipientName> — <ShortTopic>",
    "body": "Hi <RecipientName>\n\nPlease join the Zoom call at <ZoomLink> on <LocalDateTime>.\n\n<UserMessage>\n\nRegards,\n<Signature>"
  },
  {
    "name": "Follow-up Reminder",
    "category": "Follow-ups",
    "subject": "Following up on our previous conversation",
    "body": "Hi <RecipientName>\n\nI wanted to follow up regarding <UserMessage>. Please let me know your thoughts.\n\nBest Regards,\n<Signature>"
  },
  {
    "name": "Thank You Note",
    "category": "General",
    "subject": "Thank you for your time",
    "body": "Hi <RecipientName>\n\nThank you for <UserMessage>. It was a pleasure working with you.\n\nWarm Regards,\n<Signature>"
  },
  {
    "name": "Forward with FYI",
    "category": "General",
    "subject": "Fwd: <OriginalSubject>",
    "body": "Hi <RecipientName>\n\nForwarding this for your reference.\n\n<UserMessage>\n\nRegards,\n<Signature>"
  },
  {
    "name": "Share Meeting Notes",
    "category": "Meetings",
    "subject": "Meeting Notes - <Date>",
    "body": "Hi All\n\nHere are the notes from our meeting on <Date>:\n\n<UserMessage>\n\nRegards,\n<Signature>"
  }
]
```

---

## 20) File Index
- **ui_flow.svg** — UI navigation flow.  
- **ui_mockup_layout.svg** — Main layout wireframe.  
- **architecture.svg** — Component architecture.  
- **requirement.md** — This document.
