# Chatthreads

This is a chat system backend that supports threaded messages, DMs, mentions, suspensions, and community channels — kind of like a stripped-down Slack or Discord clone. Everything’s driven by a relational DB and built in Python with a bunch of small APIs for core functionality.

## What it does

- Users can message each other directly or in channels within communities.
- Messages can be replies (i.e. threads), and support `@mentions`.
- Suspensions are handled per-community (or globally in some cases).
- Tracks unread messages and lets users fetch only what they haven’t seen.
- There's a full-text search setup for digging through chat history.
- Usernames can be changed, but there's a 6-month cooldown between changes.

## Stuff to know

- This is backend-only. No frontend — just API methods.
- The DB schema evolves across iterations, and we have seed data to test against.
- APIs are tested using Python’s `unittest`, and test data is loaded before each run.
- Most of the work happens in the `src/` folder. Tests are in `tests/`.

## Running tests

```bash
python3 -m unittest discover tests/
```

Make sure you’ve got PostgreSQL set up locally and the test database seeded.

## Current focus

Right now, the project includes:
- Message handling (send, read, list)
- User state (suspensions, username history)
- Channel and community setup
- Search and analytics endpoints
