# Scope and proposal: meeting_a

> STATUS: DRAFT. Not approved. Must not be sent to the client.

## 1. Requirements, platform check and estimate

### REQ-001: Add search filters allowing users to narrow results by category and city
- Client said: "I want them to narrow it down by category and by city." (status: confirmed)
- Platform check: existing_configuration. The platform already provides built‑in category and city filters via URL patterns and top‑level category filter
  - source: https://support.brilliantdirectories.com/support/solutions/articles/12000103849-my-members-search-members-search-filters
  - source: https://support.brilliantdirectories.com/support/solutions/articles/5000682653-how-to-edit-the-seo-settings-of-dynamic-search-results-pages
- Estimate: 11.0 / 18.0 / 26.0 h (low / likely / high)
- Acceptance criterion (confirm with client): When a user selects a category, a city, or both from the search filters, the system displays only the results that match the selected category and/or city criteria.

### REQ-002: Streamline the member addition process to reduce manual admin effort
- Client said: "Adding members. Right now I add every new business by hand from the admin, about thirty a week. It takes hours." (status: confirmed)
- Platform check: needs_clarification. Knowledge Brain returned 'insufficient_evidence'. A missing result does not prove the feature is absent: ask a human expert.
- Estimate (PROVISIONAL): 21.0 / 28.0 / 34.0 h (low / likely / high)
- Acceptance criterion (confirm with client): The member addition workflow shall be completed with no more than three user interactions (clicks or form submissions) and without requiring manual data entry beyond uploading a prepared CSV file, achieving at least a 50% reduction in manual steps compared to the current process.

### REQ-003: Implement a monthly newsletter that is sent only to members who have opted in
- Client said: "I want to send a newsletter to all members once a month." (status: confirmed)
- Platform check: existing_limited. Shows opt‑in tracking but doesn't confirm monthly newsletter scheduling
  - source: https://support.brilliantdirectories.com/support/solutions/articles/12000109094-install-user-consent-tools-gdpr-dashboard-installer
- Estimate: 17.0 / 30.0 / 47.0 h (low / likely / high)
- Acceptance criterion (confirm with client): The system must automatically send the monthly newsletter each month exclusively to members whose account records indicate an active opt‑in status, and must not send the newsletter to any members without such opt‑in confirmation.

### REQ-004: Fix the mobile homepage layout so the menu does not overlap the logo and looks good on phones
- Client said: "The homepage looks terrible on phones. The menu overlaps the logo." (status: confirmed)
- Platform check: needs_clarification. Knowledge Brain returned 'insufficient_evidence'. A missing result does not prove the feature is absent: ask a human expert.
- Estimate (PROVISIONAL): 8.0 / 14.0 / 22.0 h (low / likely / high)
- Acceptance criterion (confirm with client): When viewed on any mobile device with a viewport width between 320 px and 480 px, the homepage header must display the logo fully visible with no overlap from the navigation menu.

## 2. Totals

- Hours (low / likely / high): 57.0 / 90.0 / 129.0
- Cost at placeholder 40.0/h USD: 2280 / 3600 / 5160 (NOT a quote)
- Client budget: 3000 USD
- WARNING: likely cost exceeds the client's stated budget. Discuss scope or phasing.

## 3. Constraints stated by the client

- budget: $3000
- deadline: end of November 2026

## 4. Assumptions and risks

- Estimates are provisional where the platform check was inconclusive: REQ-002, REQ-004
- The hourly rate is a placeholder; taxes and currency are not decided.

## 5. Open questions

- Do you prefer an automated bulk‑import tool for new members, a self‑service registration portal, or both?
- How should the category hierarchy be defined for the search filters?
- Which email service provider or system should be used to send the monthly newsletter?
- Which platform/technology stack is the current site built on?

## 6. Exclusions

- Reviewer must list anything the client explicitly excluded before approval.
