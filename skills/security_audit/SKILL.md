---
name: security_audit
version: 1.0.0
description: Automated security inspection routine checking AST dangerous calls, secrets, and permissions.
author: kuroLabs-ai
tags: [security, audit, ast, compliance]
---

# Automated Security Audit Routine

Systematic security audit procedure for inspecting codebases before releases.

## Steps:
1. **Secret Scanning**: Check for accidental API keys, tokens, or credentials across tracked files.
2. **AST Analysis**: Scan Python source for unauthorized `os.system`, `subprocess`, or low-level primitives.
3. **Permission Boundary**: Verify sensitive actions are gated by Safe Mode confirmation prompts.
4. **Report**: Compile and emit a structured security audit report.
