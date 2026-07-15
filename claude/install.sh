#!/usr/bin/env bash
# Install Claude configs from this repo into ~/.claude via a symlink.
# Symlinks write through, so refining a skill while working edits the repo
# files directly (then commit & push).
#
# Usage: bash claude/install.sh

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_skills="$repo_root/skills"
claude_dir="${HOME}/.claude"
dst_skills="$claude_dir/skills"

if [ ! -d "$repo_skills" ]; then
  echo "Cannot find $repo_skills - run this from the ai-configs repo." >&2
  exit 1
fi

mkdir -p "$claude_dir"

if [ -e "$dst_skills" ] || [ -L "$dst_skills" ]; then
  if [ -L "$dst_skills" ]; then
    echo "skills symlink already exists -> $(readlink "$dst_skills"). Re-creating."
    rm "$dst_skills"
  else
    echo "$dst_skills already exists as a real folder. Move/merge its contents into $repo_skills first, then re-run." >&2
    exit 1
  fi
fi

ln -s "$repo_skills" "$dst_skills"
echo "Linked $dst_skills  ->  $repo_skills"
echo "Installed skills:"
find -L "$dst_skills" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;
