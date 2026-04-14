---
name: caption-subtitle-formatter
description: Formats captions and subtitles for readability, timing, and accessibility across videos. Use when the user asks to format subtitles, create captions, split transcript into caption blocks, or improve subtitle readability.
---

# Caption & Subtitle Formatter

## Overview

Ensures captions are readable, timed correctly, and maintain visual clarity.

**Keywords**: caption, subtitle, accessibility, readability, video

## Instructions

1. Accept raw transcript or spoken content from the user
2. Break text into caption blocks of 1–2 lines (max ~42 characters per line)
3. Align caption timing to natural speech pauses
4. Ensure proper punctuation for readability without audio
5. Flag long sentences for splitting and remove filler words (um, uh) if appropriate

## Output Format

- Numbered caption blocks
- Timing cues in [HH:MM:SS] format (if provided)
- Clean, formatted text per block

## Constraints

- Avoid long lines — keep captions scannable
- Each block should represent one complete thought
- Maintain clarity for viewers watching without sound
