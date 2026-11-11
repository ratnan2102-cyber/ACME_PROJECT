# Tool comparison — Acme backend

This is an implementation comparison with the course reference project, not a controlled benchmark
of multiple coding agents. The reference README reports 33 tests; this build currently passes 56.

## What this Copilot build did better

It added broader automated coverage for combined filters, pagination boundaries, status persistence,
and validation errors than the reference's published 33-test suite.

## Where this Copilot build did worse

The course repository uses one shared requirements file, while this initially empty workspace now
has a standalone `requirements.txt`. That makes setup self-contained, but it creates another place
for dependency versions to drift.
