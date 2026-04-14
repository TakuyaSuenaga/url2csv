---
name: code-review-skill
description: Reviews code for bugs, inefficiencies, and adherence to best practices, providing actionable improvement suggestions. Use when the user asks to review code, find bugs, check for security issues, optimize performance, or assess code quality.
---

# Code Review Skill

## Overview

Analyzes code to ensure quality, efficiency, and maintainability.

**Keywords**: code, review, bugs, optimization, best practices

## Instructions

1. Accept the code snippet or file from the user (include language context)
2. Analyze the code for:
   - Bugs and logical errors
   - Security vulnerabilities (injection, exposure, etc.)
   - Performance inefficiencies
   - Readability and naming clarity
   - Adherence to language best practices
3. List issues found with severity ratings (critical / warning / suggestion)
4. Provide specific, actionable fix recommendations for each issue
5. Optionally provide a revised version of the code

## Output Format

- Issues found (severity: critical / warning / suggestion)
- Suggested fix per issue
- Optional: revised code block

## Constraints

- Maintain accuracy — do not flag false positives
- Prioritize security and correctness over style
- Be specific; avoid vague feedback like "improve this"
