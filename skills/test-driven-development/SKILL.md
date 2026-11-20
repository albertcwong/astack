---
name: test-driven-development
description: Use when implementing a testable behavior change or fixing a regression. Drive the change with a focused test that fails before the fix and passes after it.
---

# Test-driven development

Start with one observable requirement. Find a nearby test, its runner and the command for running just that case. Use the smallest boundary that can actually fail for this reason: a parser test for an input rule, an integration test for persistence, a browser test for browser behavior. Do not introduce a new framework if the project already exercises that boundary.

1. **Red:** Write the example in the consumer's terms. For a CLI promising to reject an invalid flag, assert the exit status and useful error, not which helper ran. Run it on the unmodified implementation. Check that it fails because the promised behavior is missing, not because setup or imports broke. If it already passes, revisit the reproduction before changing code.
2. **Green:** Make the smallest implementation change that satisfies the requirement. Run the same test unchanged. Prefer real values and isolated fixtures; substitute for expensive or external systems at their boundary, not for the code under test.
3. **Refactor:** Clean up while the test stays green. Run neighboring cases and the project's applicable checks. Use the project's end-to-end verification when a passing unit test alone cannot prove the user-visible result.

For a fix already in progress, demonstrate the new test on a separate clean pre-fix checkout or snapshot. Do not reset a shared tree. Report the command, the failure observed before the fix, and the result after it. If you only observed green, say so.
