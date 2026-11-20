---
name: deprecation-and-migration
description: Use when retiring or replacing a public API, CLI flag, config key, dependency or persisted format that existing consumers may still rely on.
---

# Deprecation and migration

Identify who consumes the old behavior, including older clients and saved data. Search known callers, examples and fixtures, but do not treat an empty repository search as proof that external callers are gone. Decide whether the old behavior is discouraged or scheduled for removal. Follow the project's compatibility and release policy.

1. **Ship a working replacement first.** Document the old and new forms side by side. For a renamed flag, route both spellings to the same implementation and test both. Define what happens if callers supply both. Keep warnings separate from machine-readable output.
2. **Give callers a path and a window.** Publish a migration example, who to contact, and the approved removal version or criterion. If there is no date, say so. Record the change using the project's changelog and versioning convention.
3. **Move callers in reversible steps.** For stored data, add a compatible reader or schema before changing writers. Rehearse on synthetic old and new fixtures; check mixed-version operation, restart after a partial migration, and whether rollback can still read newly written data. If rollback cannot, document the recovery plan before rollout.
4. **Remove only after the agreed gate.** Check supported consumers, adoption evidence and the end of the compatibility window. Missing telemetry is not zero usage. If evidence or approval is missing, leave compatibility in place and name the blocker. Remove old entry points, warnings and stale examples together once approved.

Report what remains supported and how to verify migration or recovery. Planning a migration does not authorize a production backfill, destructive schema change or release.
