# Specification - Track: Capture Service & Email Processing

## Overview
Create a 'Capture' service that parses natural language input into the Inbox table, enabling frictionless ubiquitous capture for the GTD system. This includes building basic Email-to-Task processing via IMAP polling, alongside HTTP API and CLI interfaces.

## Functional Requirements
- **Input Interfaces:**
  - **API Endpoint:** An HTTP endpoint to receive plain text capture payloads.
  - **CLI Command:** A command-line script to quickly send text to the capture service.
  - **Email Ingestion:** A background service/script that polls an email inbox via IMAP and extracts the subject/body as captured items.
- **Parsing Engine (Basic Regex/Heuristics):**
  - Extract basic GTD metadata from the input string (e.g., `#tag` or `@context`).
  - Strip unnecessary email signatures or formatting from ingested emails.
- **Inbox Integration:**
  - Parsed inputs must be saved as new records in the `Inbox` table (using existing CRUD functions).
  - Set the `source_tag` appropriately (e.g., `api`, `cli`, `email`).
- **Error Handling:**
  - If parsing fails to extract specific metadata, the system must gracefully degrade and save the entire input as a "Raw Inbox Item" for manual clarification later.

## Non-Functional Requirements
- **Performance:** The API and CLI must respond within 5 seconds to uphold the "frictionless" GTD pillar.
- **Security:** Email credentials (IMAP) must be handled securely (e.g., via environment variables).

## Acceptance Criteria
- A user can capture an item via a local CLI command.
- A user can send an HTTP POST request to capture an item.
- The system can connect to a mock/real IMAP server, read an unread email, and save it to the Inbox table.
- All captured items are correctly persisted in the SQLite database as `Inbox` records.

## Out of Scope
- Advanced AI/LLM-based intent extraction.
- Fully automated routing bypassing the Inbox (all items must land in the Inbox first for "Clarifying").