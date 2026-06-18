# Database / Storage Diagram Not Applicable

The inspected repository does not contain a database schema, ORM configuration, migration files, or database service configuration. DocuLingua stores files locally instead:

- Uploaded source documents are stored under `app/storage/uploads/`.
- Generated PDF learning guides are stored under `app/storage/outputs/`.
- Cache-related placeholder storage exists under `app/storage/cache/`.
- Runtime configuration is stored in `.env`.

Because the MVP does not use a database, an ER diagram is not applicable. A local storage view is included in the architecture diagram.
