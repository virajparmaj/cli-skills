# Functional Testing Checklist

Use this checklist to design and execute functional tests for sections `1.1` to `1.9`.

For each case, capture:
- preconditions
- action
- expected behavior
- actual behavior
- evidence (logs, timestamps, screenshots, request IDs)

## 1.1 End-to-end user flows

Core scenarios:
- Signup flow including email or OTP verification paths
- Login and logout flow with correct session transitions
- Checkout or payment flow with success and failure branches
- Upload flow including validation and post-upload state updates

Failure and edge checks:
- Invalid credentials, expired links, already-used tokens
- Partial completion followed by resume
- Retry after transient failure

## 1.2 Navigation and routing correctness

Core scenarios:
- Route-to-screen mapping works for all primary entry points
- Deep links open the intended screen and state
- Guarded routes redirect correctly for unauthenticated and unauthorized users

Failure and edge checks:
- Broken links, stale route params, unknown routes
- Route changes during pending requests

## 1.3 Button, link, modal, dropdown interactions

Core scenarios:
- Primary CTAs execute exactly once per intended click
- Links navigate to expected destinations
- Modals open, close, and restore focus correctly
- Dropdowns show expected options and persist selected state

Failure and edge checks:
- Rapid repeated clicks
- Action during loading state
- Escape-key and outside-click behavior for dialogs

## 1.4 Multi-step workflows and interruptions

Core scenarios:
- Wizard-style flows preserve progress between steps
- Required validations prevent invalid progression
- Session timeout handling inside multi-step flows

Failure and edge checks:
- Interrupt flow mid-step, then resume
- Switch tabs/windows and continue
- Network retry during step transition

## 1.5 Back button, refresh, duplicate-click behavior

Core scenarios:
- Browser back/forward keeps state consistent
- Refresh preserves or safely resets state according to product rules
- Duplicate-click protection prevents duplicate orders/uploads/requests

Failure and edge checks:
- Refresh during pending mutation
- Back navigation after completion pages
- Re-submission of prior requests from history

## 1.6 Search, filter, and sort functionality

Core scenarios:
- Search returns expected results for exact, partial, and empty queries
- Filters combine correctly and reflect active state
- Sort order remains stable with pagination and updates

Failure and edge checks:
- Invalid filter values and unsupported query params
- Large result sets and slow responses
- No-result and reset behavior

## 1.7 Admin and restricted flows

Core scenarios:
- Admin-only actions are available only to valid admin roles
- Standard users cannot access restricted UI or API operations
- Role changes take effect without stale authorization state

Failure and edge checks:
- Direct URL access attempts to restricted routes
- Token tampering or stale-session replay
- Inconsistent frontend and backend authorization decisions

## 1.8 File upload, download, import, and export flows

Core scenarios:
- Allowed file types upload and process successfully
- Downloads produce complete, correct files
- Import pipeline validates format, schema, and duplicates
- Export output matches selected filters and date ranges

Failure and edge checks:
- Oversized files, malformed files, unsupported formats
- Interrupted upload/download and resume behavior
- Permission checks for private files

## 1.9 ML/AI feature execution (if applicable)

Core scenarios:
- AI feature triggers correctly from user actions
- Request lifecycle states are visible (queued, running, complete, failed)
- Fallback behavior is correct when model/API is unavailable

Failure and edge checks:
- Retry behavior, timeout handling, and duplicate prompts
- Safety or policy guardrail behavior on disallowed input
- Input/output traceability for incident debugging

## 1.10 API response contract testing (if applicable)

Core scenarios:
- API responses match documented schemas and types
- Unexpected extra fields are handled gracefully (not crash or error)
- Missing expected fields trigger clear fallback or error behavior
- API version mismatches produce actionable errors, not silent failures

Failure and edge checks:
- Stale cached responses after schema changes
- Partial response objects from interrupted connections
- Rate-limited or throttled responses

## 1.11 Notification and email flow testing (if applicable)

Core scenarios:
- In-app notifications trigger on correct events and display accurately
- Email delivery triggers fire for expected actions (signup, password reset, order confirmation)
- Notification preferences and unsubscribe flows work correctly

Failure and edge checks:
- Duplicate notifications from retried actions
- Notification display with missing or malformed content
- Email delivery failures and user-visible feedback

## 1.12 Real-time and WebSocket feature testing (if applicable)

Core scenarios:
- WebSocket or SSE connections establish and maintain correctly
- Real-time updates appear promptly in the UI
- Reconnection after disconnection preserves or recovers state

Failure and edge checks:
- Message ordering after reconnection
- Stale data display during connection gaps
- Server-side connection limits and graceful degradation
- Concurrent connections from multiple tabs or devices

## 1.13 Internationalization and localization testing (if applicable)

Core scenarios:
- Language switching applies to all visible text without page reload issues
- RTL layouts render correctly for RTL languages
- Date, time, number, and currency formatting matches locale

Failure and edge checks:
- Missing translations show fallback text, not empty strings or keys
- Text overflow and truncation in translated strings (longer than English)
- Locale-dependent sorting and filtering behavior
