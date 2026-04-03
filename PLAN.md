# AI Changelist Versioning System (ai-changelist)

## Overview
A lightweight CLI tool for tracking, versioning, and managing AI prompt engineering sessions alongside the resulting code changes. It acts as a specialized version control system designed to document the iterative relationship between prompts and the code they produce. 

Each changelist inherently captures:
- The original AI prompt used to generate the changes (optional but highly recommended).
- A detailed list of files changed, complete with pre- and post-content diffs.
- An accurate timestamp of when the change was applied.
- Branching context to support experimenting with different prompt paths.
- A **Parent changelist** pointer to maintain a strict genealogical history of changes, allowing for exact history tracking and reconstruction.

## Core Concepts & Features

### 1. Initialization and Baseline Tracking
- **`ai-cl init`**: To start tracking, the system must be initialized. This command scans the current files and code in the directory and establishes a "baseline" or root parent changelist. All subsequent AI edit trackers will trace their lineage back to this baseline.

### 2. Parent-Aware History Tracking
- Every changelist knows its parent (or parents, in the case of a merge). This graph-based architecture, similar to Git versioning, ensures that an exact sequence of prompts and their delta changes can be mapped out chronologically or visually over time with branches.

### 3. Experimental Branching
- **Branching System**: AI experiments often require trying multiple prompt variations. The tool supports creating branches (`ai-cl branch <name>`) to isolate experimental prompts without affecting the primary codebase path. You can instantly create and switch to a new branch using `ai-cl checkout -b <name>`. Branches can be checked out, worked on, and eventually merged back.

### 4. Selective Changelist Removal
- **`ai-cl remove <id>`**: Need to undo a specific hallucination or bad AI suggestion? This feature allows the user to remove a specific changelist from the codebase. It attempts to revert the text changes introduced in that exact changelist and cleanly excises only that specific node from the active change history, keeping the rest of the graph intact.

---

## Data Model
```json
{
  "id": "string (UUID v4)",
  "timestamp": "ISO 8601 timestamp",
  "prompt": "string (original AI prompt)",
  "branch": "string (current active branch name)",
  "parent_id": "string (UUID of the parent changelist / baseline)",
  "tags": "array of strings",
  "files_changed": [
    {
      "path": "string",
      "action": "create|modify|delete",
      "content_before": "string or null",
      "content_after": "string or null",
      "diff": "string (unified diff)"
    }
  ]
}
```

## Storage Format
- Stored as JSON files localized within a `.ai-changelist/` directory.
- Individual changelists: `.ai-changelist/changelists/{id}.json`.
- State tracking (current branch, HEAD): `.ai-changelist/HEAD.json`.
- Configuration settings: `.ai-changelist/config.json`.

---

## Commands Reference

### Initialization & State Building
```text
ai-cl init
    Initializes the workspace. Takes a snapshot of the current files, sets it as the baseline "parent" changelist, and auto-appends `.ai-changelist/` to the repository's `.gitignore`.
```

### Core Usage
```text
ai-cl status
    List files that have been modified since the last saved changelist.

ai-cl diff [id]
    Preview the unified diff of current working directory changes against HEAD. If an [id] is provided, show the diff for that specific historical changelist.

ai-cl save [--prompt "text"] [--file prompt.txt]
    Calculate diffs from the current state against the HEAD, save them as a new changelist, and advance HEAD.

ai-cl list [--limit N] [--branch name] 
    Display a chronological history of changelists along with their brief prompts and timestamps.

ai-cl show <id>
    Display full details, prompt text, and inline unified diffs for a specific changelist.
```

### History Management & Reversions
```text
ai-cl remove <id>
    Revert the code changes introduced by a specific changelist and remove only that node from the historical chain, preserving the other nodes.

ai-cl restore <id> [--file path]
    Restores specific files to the state they were in at the given changelist ID.
```

### Prompt Experimentation (Branching)
```text
ai-cl branch
    List all branches and highlight the currently active branch.

ai-cl branch <name>
    Create a new prompt experiment branch starting from the current changelist.

ai-cl branch -d <name>
    Delete a specific experimental branch.

ai-cl checkout <branch>
    Switch the workspace to the tip of another branch.

ai-cl checkout -b <branch>
    Create a new branch and immediately switch to it to start working.

ai-cl merge <branch>
    Merge an experimental branch back into the current branch.
```

---

## Implementation Plan

### Phase 1: Foundation & Baseline Initialization
- [ ] Project setup & basic CLI framework (e.g., `argparse` or `click`).
- [ ] Implement `.ai-changelist/` repository structure.
- [ ] Build the `ai-cl init` command to map existing code to a baseline state file and append to `.gitignore`.
- [ ] Define the JSON data model encompassing `parent_id` tracking.

### Phase 2: Core Changelist Tracking
- [ ] Implement robust file diffing mechanisms (`difflib`).
- [ ] Implement `ai-cl status` and `ai-cl diff` to preview unsaved changes.
- [ ] Build `ai-cl save` to record AI prompts, determine file deltas, and link to current `parent_id`.
- [ ] Implement history traversal: `ai-cl list` and `ai-cl show`.

### Phase 3: Targeted History Modification (Removal)
- [ ] Implement algorithm for cleanly reverting patches of a historical changelist.
- [ ] Build `ai-cl remove <id>` command.
- [ ] Implement standard `ai-cl restore` for reverting individual files to past states.

### Phase 4: Branching & Experimentation
- [ ] Add branch pointers to data models.
- [ ] Build `branch` (create/list/delete) and `checkout` commands to navigate the workspace.
- [ ] Build `merge` command (basic text conflict handling or defer to git).

### Phase 5: AI Agent Integration
- [ ] Create an agent skill definition (e.g., `SKILL.md`) for easy integration to other AI agent coding tools.
- [ ] Document stable CLI interfaces and programmatic usage patterns specifically for AI agents.