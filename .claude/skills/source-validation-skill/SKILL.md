---
name: source-validation-skill
description: Validates the credibility of information sources, highlighting reliability, relevance, and potential biases. Use when the user asks to verify a source, check if information is credible, evaluate bias in references, or assess the reliability of research material.
---

# Source Validation Skill

## Overview

Filters information for trustworthiness and relevance.

**Keywords**: credibility, validation, sources, research, bias

## Instructions

1. Accept a list of sources or a piece of content with citations from the user
2. Evaluate each source for author credibility, publication date, and domain authority
3. Detect potential biases (political, commercial, ideological)
4. Rate each source for reliability (high / medium / low)
5. Highlight the most trustworthy sources and flag questionable ones

## Output Format

- Source list with reliability ratings
- Key concerns or biases noted per source
- Recommended sources for further reading

## Constraints

- Avoid using unverified information in outputs
- Prioritize peer-reviewed, authoritative, or primary sources
- Be explicit about uncertainty when reliability cannot be determined
