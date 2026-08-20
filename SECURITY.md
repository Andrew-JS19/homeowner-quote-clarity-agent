# Security policy

## Supported demonstration scope

This repository is a time-bounded hackathon demonstration that processes only bundled fictional fixtures. It is not approved for real quotations or personal data.

## Safety controls

- Source text is evidence, never an instruction channel.
- The application does not fetch URLs, execute attachments, send messages, make payments, or accept arbitrary uploads.
- Every extracted fact retains a source anchor and excerpt hash.
- Unknowns remain unknown and low-confidence values require human review.
- No contractor ranking, price-fairness decision, or legal, tax, engineering, insurance, or safety conclusion is produced.
- Cloud credentials must use Application Default Credentials or the Cloud Run service identity; secrets must never be committed.

## Reporting

Do not include credentials, private customer data, or live exploit details in a public issue. Contact the repository owner privately through the verified GitHub profile.
