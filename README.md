# AI Configs

This repository contains configuration files, templates, and instructions for AI coding assistants.

## Structure

- **.github/workflows**: GitHub Actions workflows.
- **antigravity**: Specific configurations for the Antigravity CLI.
- **claude**: Claude Code skills & config, linked into `~/.claude` (see `claude/README.md`).
- **vscode**: Configurations for VS Code based assistants (Claude, Codex).
- **project-templates**: Boilerplate setup for new projects.
- **snippets**: Reusable documentation/code snippets.

## Usage

Reference these files when setting up new projects or configuring your AI environment. 

Use symlinks to install these instructions. For example:

```bash
#!/bin/bash
# Create the directory if it doesn't exist
mkdir -p ~/.gemini

# Symlink the file from your repo to the location antigravity expects
ln -sf $(pwd)/antigravity/GEMINI.md ~/.gemini/GEMINI.md

echo "Antigravity instructions synced!"
```