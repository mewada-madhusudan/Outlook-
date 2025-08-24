
# Email Automation Desktop Tool - Requirements Document

## 1. Project Overview
The Email Automation Desktop Tool is a Python-based application designed to streamline Outlook/Office 365 email workflows using Microsoft Graph API and Zoom API.  
It reduces repetitive tasks like sending meeting invites, tracking replies, sending reminders, and managing attachments.  

Target environment: **Desktop app (Python, PyQt6)**

---

## 2. Core Features

### 2.1 Send Mail
- Compose new emails from templates or custom text
- Add recipients (To, CC, BCC)
- Auto-append signature (if saved)
- Insert Zoom meeting links automatically
- Save drafts before sending

### 2.2 Send Reminders
- Track sent mails and pending replies
- Send reminder emails with one click
- Predefined reminder templates available

### 2.3 Response Tracking
- Detect whether recipient replied via Graph API
- Show reply status in dashboard (Replied / Pending)
- Send escalation emails (optional)

### 2.4 Attachments Management
- Download attachments automatically based on rules (e.g., subject, sender)
- Save to local folder with structured naming
- Bulk download option

### 2.5 Template Library
- Predefined JSON-based templates (Zoom Invite, Follow-up, Thank You, FYI, Meeting Notes)
- Editable inside app via Template Editor
- Placeholders: `<RecipientName>`, `<ZoomLink>`, `<UserMessage>`, `<Signature>`

### 2.6 Quick Actions
- One-click shortcuts for common workflows:
  - Schedule Zoom meeting + email invite
  - Send quick “Thank You” note
  - Follow-up on pending emails
- User only enters **recipients + short message**

### 2.7 Template Editor
- Create/edit templates inside app
- Fields: Template Name, Subject, Body (with placeholders)
- Live preview pane to show rendered output
- Save templates in JSON format

---

## 3. UI / UX Design

### 3.1 UI Wireframe Layout
- **Left Navigation Panel**
  - Dashboard
  - Templates
  - Quick Actions
  - Reminders
  - Attachments
  - Settings

- **Right Content Panel**
  - Context-specific content (Template Editor, Quick Actions, Reminders table)

### 3.2 Template Editor UI
- Input fields for Template Name, Subject, Body
- Placeholder dropdown to insert variables
- Preview pane to show final rendered email

### 3.3 Mockup Example
![UI Mockup Layout](ui_mockup_layout.png)

### 3.4 Flow Diagram
![UI Flow Diagram](ui_flow_diagram.png)

ASCII Version:

```
Login (MS/Zoom OAuth)
        |
        v
   Dashboard (Main Menu)
   ├── Templates (List + Editor) → Draft Window (Review + Send)
   ├── Quick Actions (Zoom, Follow-up, Thank You) → Draft Window
   ├── Reminders (Track Replies, Send Reminder) → Draft Window
   ├── Attachments (Rules + Save)
   └── Settings (Signature, Accounts)
```

---

## 4. APIs and Integrations

### 4.1 Microsoft Graph API (Email Integration)
- `/me/sendMail`
- `/me/messages`
- `/me/mailFolders/inbox/messages`
- `/me/events` (for calendar integration)

### 4.2 Zoom API (Meetings)
- Create meeting endpoint: `POST /users/me/meetings`
- Get meeting details for link insertion

---

## 5. Data Model

### 5.1 Local Storage (SQLite)
- `templates` table (id, name, subject, body, created_at, updated_at)
- `emails` table (id, recipient, subject, body, sent_time, status)
- `reminders` table (id, email_id, reminder_time, status)
- `attachments` table (id, email_id, file_name, file_path)

---

## 6. Security
- Use OAuth2.0 for Microsoft Graph + Zoom APIs
- Store tokens securely in encrypted local storage
- Follow Microsoft recommended token refresh flow

---

## 7. Example Templates (JSON)

```json
[
  {
    "name": "Zoom Invite",
    "subject": "Meeting Invitation: {topic}",
    "body": "Hi {recipient},\n\nPlease join the Zoom call at {zoom_link}.\n\nRegards,\n{signature}"
  },
  {
    "name": "Follow-up",
    "subject": "Gentle Reminder: {topic}",
    "body": "Hi {recipient},\n\nJust following up on my previous email regarding {topic}.\n\nRegards,\n{signature}"
  },
  {
    "name": "Thank You Note",
    "subject": "Thank you for your time",
    "body": "Hi {recipient},\n\nThank you for taking the time to connect today.\n\nRegards,\n{signature}"
  },
  {
    "name": "Forward with FYI",
    "subject": "FYI: {topic}",
    "body": "Hi {recipient},\n\nSharing the below for your reference.\n\nRegards,\n{signature}"
  },
  {
    "name": "Meeting Notes",
    "subject": "Notes from Meeting: {topic}",
    "body": "Hi {recipient},\n\nPlease find below the notes from our meeting:\n{notes}\n\nRegards,\n{signature}"
  }
]
```

---

## 8. Development Milestones
1. Setup project structure (PyQt6 UI + SQLite + Graph Auth)
2. Implement Send Mail & Template Library
3. Add Quick Actions & Template Editor
4. Add Reminders & Response Tracking
5. Implement Attachments Download
6. Polish UI (Mockup layout integration)
7. Testing & UAT

---

## 9. Acceptance Criteria
- User can send emails using templates and quick actions
- User can create/edit templates via Template Editor
- Reminders trigger for pending replies
- Attachments downloaded as per rules
- Zoom links auto-inserted in meeting invites
- Secure authentication via OAuth2.0

---

**End of Document**
