# 🚀 AI Changelist (`ai-cl`)

A specialized, lightweight CLI tool designed to track, version, and manage AI prompt engineering sessions alongside the resulting code changes. It acts as a localized version control system tailored specifically for documenting the iterative relationship between AI prompts and the code they produce over time via a graph-based history architecture.

## 🌟 Key Features

- **Prompt Integration**: Save your raw AI prompts attached directly to the exact file diffs they generated.
- **Experimental Branching**: Spin up multiple prompt-testing paths (`ai-cl checkout -b <name>`) natively without muddying your primary git tree. Test out complex AI refactors safely.
- **State Shadowing**: The pure Python `difflib` backend calculates exact file deltas efficiently (`ai-cl status`) while natively respecting your repository's `.gitignore` rules via `pathspec`.
- **Targeted Excision**: Need to undo a massive hallucination? Cleanly rip out specific node updates.
- **Zero-Dependency Ready**: Completely usable via `pipx` or as downloaded compiled standalone binaries across Windows, Linux, and macOS.

## 📦 Installation

This tool provides ultimate distribution flexibility. 

### Option A: Python (`pip`)
```bash
# Clone the repository
git clone https://github.com/your-username/ai-changelist.git
cd ai-changelist

# Install the global 'ai-cl' CLI tool using pip
pip install .
```

### Option B: Standalone Binaries
Head over to the [Releases](https://github.com/your-username/ai-changelist/releases) page and download the auto-compiled executable for Windows, Linux, or macOS to run it entirely detached from a Python footprint!

## 💻 Quick Usage Guide

**Initialize** the tracker in your codebase. This establishes a baseline and auto-adds `.ai-changelist` to your `.gitignore`:
```bash
ai-cl init
```

Make changes using your favorite AI Agent, then **verify** the raw changes:
```bash
ai-cl status
ai-cl diff
```

**Save** those changes directly alongside the prompt:
```bash
ai-cl save -m "Implement a responsive CSS grid layout for the dashboard."
```

Explore your AI-generated **history** with beautifully modeled formatting:
```bash
ai-cl list
ai-cl show <uuid-or-prefix>
```

Testing something risky? Create an **experimental branch**:
```bash
ai-cl checkout -b "test-refactor"
```

## 🤝 Roadmap & Contribution
Review `PLAN.md` to see the ideation and architectural phasing for advanced features like AI Agent Toolkit Integration, Merge heuristics, and more. Pull requests are welcome!
