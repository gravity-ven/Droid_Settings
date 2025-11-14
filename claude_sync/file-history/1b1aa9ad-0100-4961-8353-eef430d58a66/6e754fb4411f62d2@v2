#!/usr/bin/env python3
"""
DROID CLI - Command-line interface for managing DROIDs
"""

import sys
import os
import subprocess
from pathlib import Path
from droid_loader import DROIDLoader
import json


class DROIDCli:
    """CLI interface for DROID management"""

    def __init__(self):
        # Add current directory to Python path for imports
        sys.path.insert(0, str(Path(__file__).parent))
        self.loader = DROIDLoader()
        self.loader.load_droids()

    def list_droids(self, verbose=False):
        """List all available DROIDs"""
        droids = self.loader.list_droids(verbose=verbose)

        if not droids:
            print("No DROIDs found.")
            print(f"\nCreate your first DROID:")
            print(f"  droid create my-droid")
            return

        if verbose:
            print(json.dumps(droids, indent=2))
        else:
            print("\n🤖 Available DROIDs:\n")
            print(f"{'Name':<25} {'Scope':<10} {'Proactive':<10} Description")
            print("-" * 90)
            for droid in droids:
                proactive = "✓" if droid.get('proactive') else ""
                desc = droid.get('description', '')[:45]
                print(f"{droid['name']:<25} {droid['scope']:<10} {proactive:<10} {desc}")

            print(f"\n📊 Total: {len(droids)} DROIDs")
            print(f"\nUse 'droid info <name>' for detailed information")

    def show_droid_info(self, name):
        """Show detailed information about a specific DROID"""
        droid = self.loader.get_droid(name)

        if not droid:
            print(f"❌ DROID '{name}' not found")
            print(f"\nAvailable DROIDs:")
            self.list_droids()
            return 1

        print(f"\n🤖 DROID: {droid.name}\n")
        print(f"Description: {droid.description}")
        print(f"Scope: {droid.scope}")
        print(f"Model: {droid.model}")
        print(f"Proactive: {'Yes' if droid.proactive else 'No'}")

        if droid.tools:
            print(f"Tools: {', '.join(droid.tools)}")
        else:
            print(f"Tools: All available")

        if droid.triggers:
            print(f"Triggers: {', '.join(droid.triggers)}")

        print(f"\nSource: {droid.source_path}")

        print(f"\n📝 System Prompt Preview:")
        print("-" * 80)
        preview = droid.system_prompt[:500]
        if len(droid.system_prompt) > 500:
            preview += "..."
        print(preview)
        print("-" * 80)

        print(f"\n💡 Usage:")
        print(f'  Ask Claude: "Use the {name} DROID to review this code"')
        print(f'  Or mention triggers: {", ".join(droid.triggers[:3]) if droid.triggers else "N/A"}')

        return 0

    def create_droid(self, name, scope="user", edit_after=False):
        """Create a new DROID template"""
        try:
            file_path = self.loader.create_droid_template(name, scope)
            print(f"✅ Created DROID template: {file_path}")
            print(f"\n📝 Next steps:")
            print(f"  1. Edit the template: droid edit {name}")
            print(f"  2. Customize the system prompt and settings")
            print(f"  3. Use the DROID: Ask Claude to use it!")

            if edit_after:
                self.edit_droid(name)

        except FileExistsError as e:
            print(f"❌ Error: {e}")
            print(f"\nUse 'droid edit {name}' to modify existing DROID")
            return 1
        except Exception as e:
            print(f"❌ Error creating DROID: {e}")
            return 1

        return 0

    def edit_droid(self, name):
        """Open a DROID file in the default editor"""
        droid = self.loader.get_droid(name)

        if not droid:
            print(f"❌ DROID '{name}' not found")
            return 1

        # Determine editor
        editor = os.environ.get('EDITOR', 'vim')

        print(f"Opening {droid.source_path} in {editor}...")

        try:
            subprocess.run([editor, droid.source_path])
            print(f"✅ DROID '{name}' edited")
            print(f"\nReload to see changes:")
            print(f"  droid reload")
        except Exception as e:
            print(f"❌ Error opening editor: {e}")
            return 1

        return 0

    def delete_droid(self, name, force=False):
        """Delete a DROID"""
        droid = self.loader.get_droid(name)

        if not droid:
            print(f"❌ DROID '{name}' not found")
            return 1

        if not force:
            response = input(f"Are you sure you want to delete '{name}'? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled")
                return 0

        try:
            os.remove(droid.source_path)
            print(f"✅ Deleted DROID '{name}'")
        except Exception as e:
            print(f"❌ Error deleting DROID: {e}")
            return 1

        return 0

    def reload_droids(self):
        """Reload all DROIDs from disk"""
        try:
            self.loader.load_droids()
            print(f"✅ Reloaded {len(self.loader.droids)} DROIDs")
            self.list_droids()
        except Exception as e:
            print(f"❌ Error reloading DROIDs: {e}")
            return 1

        return 0

    def suggest_droids(self, context):
        """Suggest DROIDs based on context"""
        suggestions = self.loader.suggest_droids(context)

        if not suggestions:
            print(f"No DROID suggestions for context: '{context}'")
            print(f"\n💡 Tip: Create proactive DROIDs with triggers to get suggestions")
            return 0

        print(f"\n🎯 Suggested DROIDs for '{context}':\n")
        for droid_name in suggestions:
            droid = self.loader.get_droid(droid_name)
            print(f"  • {droid_name}: {droid.description}")

        return 0

    def show_help(self):
        """Show help message"""
        help_text = """
🤖 DROID CLI - Manage your Claude Code DROIDs

Usage:
  droid <command> [arguments]

Commands:
  list, ls              List all available DROIDs
  list -v, ls -v        List DROIDs with verbose output
  info <name>           Show detailed information about a DROID
  create <name>         Create a new DROID template (user scope)
  create <name> -p      Create a new DROID template (project scope)
  edit <name>           Edit a DROID in your default editor
  delete <name>         Delete a DROID
  reload                Reload all DROIDs from disk
  suggest <context>     Suggest DROIDs based on context
  help, -h, --help      Show this help message

Examples:
  droid list                          # List all DROIDs
  droid info security-auditor         # Show security-auditor details
  droid create api-tester             # Create new DROID
  droid edit code-reviewer            # Edit code-reviewer DROID
  droid suggest "security review"     # Get DROID suggestions

DROID Locations:
  User DROIDs:    ~/.claude/droids/
  Project DROIDs: .claude/droids/

For more information, visit: https://docs.claude.com
"""
        print(help_text)


def main():
    """Main CLI entry point"""
    cli = DROIDCli()

    if len(sys.argv) < 2:
        cli.show_help()
        return 0

    command = sys.argv[1]

    # Handle commands
    if command in ['help', '-h', '--help']:
        cli.show_help()
        return 0

    elif command in ['list', 'ls']:
        verbose = '-v' in sys.argv or '--verbose' in sys.argv
        cli.list_droids(verbose=verbose)
        return 0

    elif command == 'info':
        if len(sys.argv) < 3:
            print("Usage: droid info <name>")
            return 1
        return cli.show_droid_info(sys.argv[2])

    elif command == 'create':
        if len(sys.argv) < 3:
            print("Usage: droid create <name> [--project]")
            return 1
        name = sys.argv[2]
        scope = "project" if '--project' in sys.argv or '-p' in sys.argv else "user"
        edit_after = '--edit' in sys.argv or '-e' in sys.argv
        return cli.create_droid(name, scope, edit_after)

    elif command == 'edit':
        if len(sys.argv) < 3:
            print("Usage: droid edit <name>")
            return 1
        return cli.edit_droid(sys.argv[2])

    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Usage: droid delete <name>")
            return 1
        force = '--force' in sys.argv or '-f' in sys.argv
        return cli.delete_droid(sys.argv[2], force)

    elif command == 'reload':
        return cli.reload_droids()

    elif command == 'suggest':
        if len(sys.argv) < 3:
            print("Usage: droid suggest <context>")
            return 1
        context = ' '.join(sys.argv[2:])
        return cli.suggest_droids(context)

    else:
        print(f"Unknown command: {command}")
        print("Use 'droid help' for usage information")
        return 1


if __name__ == '__main__':
    sys.exit(main())
