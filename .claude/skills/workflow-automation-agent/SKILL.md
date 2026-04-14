---
name: workflow-automation-agent
description: Breaks complex tasks into step-by-step workflows, mapping actions to tools, optimizing execution, and improving efficiency. Use when the user asks to automate a process, design a workflow, break down a complex task into steps, or map out an execution plan.
---

# Workflow Automation Agent

## Overview

Converts goals into actionable workflows for AI-assisted or human execution.

**Keywords**: automation, workflow, productivity, steps, execution

## Instructions

1. Accept a high-level goal or task description from the user
2. Decompose the goal into discrete, ordered steps
3. Assign the most appropriate tool or method to each step
4. Identify parallelizable steps vs. sequential dependencies
5. Optimize the workflow for speed and minimal manual intervention

## Output Format

- Goal statement
- Step-by-step action plan (numbered)
- Tool/method assignment per step
- Dependency map (what must complete before what)

## Constraints

- Avoid vague instructions — every step must be actionable
- Maintain logical flow — no orphaned steps
- Flag steps that require human judgment or approval
