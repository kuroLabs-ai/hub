---
name: docs_generator
version: 1.0.0
description: Generate structured technical documentation from source code across multiple languages.
author: kuroLabs-ai
tags: [documentation, docs, markdown, docstrings, api-reference]
---

# Docs Generator Skill Routine

Systematic workflow routine for inspecting project source code and generating clean, comprehensive, up-to-date documentation.

## Overview
This skill guides the KuroCode AI agent through discovering modules, extracting public interfaces, docstrings, classes, methods, and configurations, and generating well-structured Markdown documentation (e.g., `README.md`, `API.md`, or `docs/` hierarchy).

## Routine Steps:

1. **Discovery & Architecture Mapping**:
   - Identify project type and primary languages (Python, TypeScript, Go, Rust, etc.).
   - Scan directory structure to discover key packages, entrypoints, modules, and exported APIs.
   - Determine documentation targets (e.g., API Reference, Architecture Overview, Getting Started, or Configuration Guide).

2. **Interface & Signature Extraction**:
   - Inspect public classes, methods, function signatures, types, and existing docstrings/JSDoc comments.
   - Flag undocumented public parameters, return types, or raised exceptions.
   - Extract CLI flags, environment variables, configuration schemas, and models.

3. **Documentation Synthesis**:
   - Draft documentation adhering to consistent heading levels, code blocks, parameter tables, and usage examples.
   - Include realistic input/output examples for critical functions and routes.
   - Add mermaid diagrams where data flows or component hierarchies need visual clarity.

4. **Cross-Reference & Validation**:
   - Verify all file paths, function signatures, and parameter names match current source code accurately.
   - Check internal markdown links and table of contents alignment.
   - Format and finalize output into target files (`docs/`, `API.md`, or updated `README.md`).
