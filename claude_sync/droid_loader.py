#!/usr/bin/env python3
"""
DROID Loader System for Claude Code
Loads, parses, and manages custom DROIDs (specialized subagents)
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re


@dataclass
class DROIDConfig:
    """Configuration for a DROID"""
    name: str
    description: str
    system_prompt: str
    model: str = "inherit"
    tools: Optional[List[str]] = None
    proactive: bool = False
    triggers: Optional[List[str]] = None
    source_path: str = ""
    scope: str = "user"  # "user" or "project"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DROIDLoader:
    """Loads and manages DROIDs from multiple locations"""

    VALID_MODELS = ["sonnet", "opus", "haiku", "inherit"]
    AVAILABLE_TOOLS = [
        "Read", "Write", "Edit", "Bash", "Glob", "Grep",
        "WebFetch", "WebSearch", "Task", "TodoWrite",
        "NotebookEdit", "AskUserQuestion", "BashOutput", "KillShell"
    ]

    def __init__(self):
        self.user_droids_dir = Path.home() / ".claude" / "droids"
        self.project_droids_dir = Path("/Users/spartan/.claude/.claude/droids")
        self.droids: Dict[str, DROIDConfig] = {}

    def _parse_droid_file(self, file_path: Path, scope: str) -> Optional[DROIDConfig]:
        """Parse a DROID markdown file with YAML frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            if not content.startswith('---'):
                print(f"Warning: {file_path.name} missing YAML frontmatter")
                return None

            # Split frontmatter and body
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"Warning: {file_path.name} invalid format")
                return None

            frontmatter = yaml.safe_load(parts[1])
            system_prompt = parts[2].strip()

            # Validate required fields
            if 'name' not in frontmatter:
                print(f"Warning: {file_path.name} missing 'name' field")
                return None

            # Validate name format
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9\-_]+$', name):
                print(f"Warning: {name} invalid (use lowercase, hyphens, underscores only)")
                return None

            # Validate model
            model = frontmatter.get('model', 'inherit')
            if model not in self.VALID_MODELS:
                print(f"Warning: {name} invalid model '{model}'")
                return None

            # Validate tools
            tools = frontmatter.get('tools')
            if tools is not None:
                if not isinstance(tools, list):
                    print(f"Warning: {name} tools must be a list")
                    return None
                invalid_tools = [t for t in tools if t not in self.AVAILABLE_TOOLS]
                if invalid_tools:
                    print(f"Warning: {name} invalid tools: {invalid_tools}")
                    return None

            # Validate description length
            description = frontmatter.get('description', '')
            if len(description) > 500:
                description = description[:497] + "..."

            # Create DROID config
            droid = DROIDConfig(
                name=name,
                description=description,
                system_prompt=system_prompt,
                model=model,
                tools=tools,
                proactive=frontmatter.get('proactive', False),
                triggers=frontmatter.get('triggers'),
                source_path=str(file_path),
                scope=scope
            )

            return droid

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def load_droids(self) -> Dict[str, DROIDConfig]:
        """Load all DROIDs from user and project directories"""
        self.droids.clear()

        # Load user-level DROIDs
        if self.user_droids_dir.exists():
            for file_path in self.user_droids_dir.glob("*.md"):
                droid = self._parse_droid_file(file_path, "user")
                if droid:
                    self.droids[droid.name] = droid

        # Load project-level DROIDs (override user-level if same name)
        if self.project_droids_dir.exists():
            for file_path in self.project_droids_dir.glob("*.md"):
                droid = self._parse_droid_file(file_path, "project")
                if droid:
                    self.droids[droid.name] = droid

        return self.droids

    def get_droid(self, name: str) -> Optional[DROIDConfig]:
        """Get a specific DROID by name"""
        return self.droids.get(name)

    def list_droids(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """List all available DROIDs"""
        if not self.droids:
            self.load_droids()

        if verbose:
            return [droid.to_dict() for droid in self.droids.values()]
        else:
            return [
                {
                    "name": droid.name,
                    "description": droid.description,
                    "scope": droid.scope,
                    "proactive": droid.proactive
                }
                for droid in self.droids.values()
            ]

    def suggest_droids(self, context: str) -> List[str]:
        """Suggest DROIDs based on context/triggers"""
        if not self.droids:
            self.load_droids()

        suggestions = []
        context_lower = context.lower()

        for droid in self.droids.values():
            if not droid.proactive:
                continue

            if droid.triggers:
                for trigger in droid.triggers:
                    if trigger.lower() in context_lower:
                        suggestions.append(droid.name)
                        break

        return suggestions

    def create_droid_template(self, name: str, scope: str = "user") -> Path:
        """Create a new DROID template file"""
        if not re.match(r'^[a-z0-9\-_]+$', name):
            raise ValueError("Name must be lowercase with hyphens/underscores only")

        target_dir = self.user_droids_dir if scope == "user" else self.project_droids_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / f"{name}.md"
        if file_path.exists():
            raise FileExistsError(f"DROID {name} already exists")

        template = f"""---
name: {name}
description: Brief description of what this DROID does
model: inherit
tools: ["Read", "Grep", "Glob"]
proactive: false
triggers: []
---

You are a specialized assistant for [specific task].

Your responsibilities:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

Guidelines:
- [Guideline 1]
- [Guideline 2]
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)

        return file_path


def main():
    """CLI interface for DROID management"""
    import sys

    loader = DROIDLoader()

    if len(sys.argv) < 2:
        print("Usage: droid_loader.py [list|load|suggest|create] [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        droids = loader.list_droids(verbose=verbose)
        print(json.dumps(droids, indent=2))

    elif command == "load":
        if len(sys.argv) < 3:
            print("Usage: droid_loader.py load <name>")
            sys.exit(1)

        loader.load_droids()
        droid = loader.get_droid(sys.argv[2])
        if droid:
            print(json.dumps(droid.to_dict(), indent=2))
        else:
            print(f"DROID '{sys.argv[2]}' not found")
            sys.exit(1)

    elif command == "suggest":
        if len(sys.argv) < 3:
            print("Usage: droid_loader.py suggest <context>")
            sys.exit(1)

        context = " ".join(sys.argv[2:])
        suggestions = loader.suggest_droids(context)
        print(json.dumps(suggestions, indent=2))

    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: droid_loader.py create <name> [--project]")
            sys.exit(1)

        name = sys.argv[2]
        scope = "project" if "--project" in sys.argv else "user"

        try:
            file_path = loader.create_droid_template(name, scope)
            print(f"Created DROID template: {file_path}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
