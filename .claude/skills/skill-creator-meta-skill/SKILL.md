---
name: skill-creator-meta-skill
description: Generates new AI skills in SKILL.md format, providing structured name, description, and instructions for future use as Agent Skills. Use when the user asks to create a new skill, add a capability as a skill file, or generate a SKILL.md for a new use case.
---

# Skill Creator (Meta Skill)

## Overview

Automates creation of Agent Skills by generating fully structured `SKILL.md` files ready for use in `.claude/skills/`.

**Keywords**: skill creation, automation, AI, modular, SKILL.md

## Instructions

1. Accept a goal or capability description from the user
2. Define the skill's purpose, role, and expected behavior
3. Generate a complete `SKILL.md` with:
   - YAML frontmatter (`name`, `description`)
   - Overview section
   - Step-by-step Instructions
   - Output Format
   - Constraints
4. Ensure `name` uses only lowercase letters, numbers, and hyphens (max 64 chars)
5. Ensure `description` clearly states what the skill does AND when to use it (max 1024 chars)

## Output Format

```
---
name: your-skill-name
description: What this skill does and when Claude should use it.
---

# Skill Name

## Overview
...

## Instructions
1. ...

## Output Format
...

## Constraints
...
```

## Constraints

- `name` must match the directory name
- `description` must include both capability and trigger condition
- Instructions must be clear and actionable
- Do not include license or external dependency references
