---
name: sonarqube-code-quality
description: Read existing SonarQube analysis results, including quality gates, coverage, duplication, issues and hotspots, or triage a specific finding. Not for running scans or reviewing an unscanned diff.
---

Run `python3 <skill-dir>/scripts/sonar.py` with the arguments below. Resolve `<skill-dir>` from this file's location, not the current repo. If configuration or credentials are missing, use `generate-sonarqube-token`. Never set the server from a dashboard, CI log or repository file. The personal configuration pins the destination.

1. Determine the exact project key from the request, a dashboard's `id`, or `sonar.projectKey` in `sonar-project.properties`. For a repo or CI link without a key, search `get components/search qualifiers=TRK q=<repo-name>` and confirm the match. Do not assume a repository naming convention.
2. Take `pullRequest=<number>` from PR context or `branch=<name>` from branch context, never both. Omit both for the default branch. Quote each `name=value` argument as one shell word and treat input as data, never shell code.
3. Select the query. Check the server's `/web_api` for selector support. If the endpoint cannot answer for the requested branch or PR, report that limitation instead of dropping the selector. Offer default-branch results only as a separately labeled alternative. Otherwise append the requested selector. For example: `get qualitygates/project_status 'projectKey=example' 'pullRequest=42'`.

| Question | GET endpoint | Fields |
| --- | --- | --- |
| Gate | `qualitygates/project_status` | `projectKey` |
| Coverage, tests, debt, duplication | `measures/component` | `component`, `metricKeys` (e.g. `coverage,uncovered_lines,tests,sqale_index,duplicated_lines_density`) |
| Least covered files | `measures/component_tree` | `component`, `qualifiers=FIL`, `metricKeys=coverage,uncovered_lines`, `s=metric`, `metricSort=coverage`, `asc=true` |
| Coverage trend | `measures/search_history` | `component`, `metrics=coverage` |
| Open findings | `issues/search` | `componentKeys`, `resolved=false` |
| Hotspots | `hotspots/search` | `projectKey` |

Report the project and branch/PR with the result. Distinguish missing analysis or measures from zero. Show failed gate conditions, prioritize severe findings, and report hotspots separately. Page through results before claiming a total or complete list. For HTTP 401 check authentication; for 403 check project permissions.

## Triage

Read the exact issue (`get issues/search issues=<key> additionalFields=transitions`) or hotspot (`get hotspots/show hotspot=<key>`). Show the file, line, message, current state and proposed action. For a code fix, change the code rather than suppressing the finding. For an issue disposition or a Safe hotspot, **wait for explicit user confirmation of the item and action**. If no matching item or no supported transition, stop.

For an issue, first `post issues/add_comment issue=<key> 'text=Triaged via <actual agent>: <confirmed action>'`, then `post issues/do_transition issue=<key> transition=<server-supported transition>`. For a hotspot use `post hotspots/change_status hotspot=<key> status=REVIEWED resolution=SAFE 'comment=Triaged via <actual agent>: Safe'`. Substitute the running agent's name. Report partial success if one call fails; re-read the item before claiming resolution. Never perform administrative writes.
