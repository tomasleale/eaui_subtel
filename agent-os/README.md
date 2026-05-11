# Agent-OS — eaui_subtel

Structured feature development with 8 specialized agents.

## Quick Start

Activate Agent-OS for a feature:
```
I'm using Agent-OS to implement {feature description}
```

## Agent Directory

### Specification Agents

- **product/** — Gather requirements through iterative questions
- **specs/** — Create detailed technical specifications

### Standard Agents

- **standards/backend/** — Backend architecture, patterns, code style
- **standards/frontend/** — Frontend components, state, UI patterns
- **standards/global/** — Security, database, deployment, infrastructure
- **standards/testing/** — Unit/integration/e2e test strategies

## Workflow: Feature Development

1. **Requirements** → Product Agent gathers needs
2. **Specification** → Specs Agent documents requirements
3. **Architecture** → Backend/Frontend/Global agents review
4. **Implementation** → Write code following standards
5. **Testing** → Testing agent guides test strategy
6. **Verification** → Ensure compliance with standards

## Config

- `config.yml` — Agent definitions and workflow
- Agents are symlinked from Claude OS templates

## Usage

**For notebook processing features:**
```
I'm using Agent-OS to implement a new data validation pipeline
- Product: collect requirements from domain experts
- Specs: define processing stages, input/output schemas
- Standards: check against existing notebook patterns
```

**For analysis features:**
```
I'm using Agent-OS to implement GSE derivation improvements
- Product: gather edge cases from EAUI 2026 data
- Specs: define algorithm with test cases
- Testing: create validation suite for expansion factors
```

## Documentation

See `.claude-os/config.json` for project metadata.
