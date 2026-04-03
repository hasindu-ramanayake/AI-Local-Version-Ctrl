#!/usr/bin/env python3
"""
AI Changelist Versioning System CLI
Track AI prompt engineering sessions and resulting code changes.
"""

import argparse
import sys
from pathlib import Path

# Ensure the root project directory is in the path so 'src.commands' imports work
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

def main():
    parser = argparse.ArgumentParser(
        description="AI Changelist Versioning System - Track AI prompt engineering sessions",
        prog="ai-cl"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize ai-changelist repository in current directory")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="List files modified since last saved changelist")
    
    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Preview unified diff of working directory changes")
    diff_parser.add_argument("id", nargs="?", help="Optional ID to diff against a historical changelist")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save current changes as a new changelist")
    save_parser.add_argument("--prompt", "-m", help="AI prompt that generated these changes")
    save_parser.add_argument("--file", "-f", help="Read prompt from file")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all changelists")
    list_parser.add_argument("--limit", "-n", type=int, help="Limit number of results")
    list_parser.add_argument("--branch", help="Filter by branch")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show changelist details")
    show_parser.add_argument("id", help="Changelist ID (or short UUID prefix)")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Revert and remove a specific changelist from history")
    remove_parser.add_argument("id", help="Changelist ID")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore files from a previous changelist")
    restore_parser.add_argument("id", help="Changelist ID")
    restore_parser.add_argument("--file", help="Restore specific file only")
    
    # Branch command
    branch_parser = subparsers.add_parser("branch", help="Manage branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name to create")
    branch_parser.add_argument("-d", "--delete", dest="delete_branch", help="Delete branch")
    
    # Checkout command
    checkout_parser = subparsers.add_parser("checkout", help="Switch branches")
    checkout_parser.add_argument("branch", help="Branch name")
    checkout_parser.add_argument("-b", action="store_true", help="Create and checkout a new branch")
    
    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge branch into current branch")
    merge_parser.add_argument("branch", help="Branch name to merge")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        from src.commands.handler import CommandHandler
        handler = CommandHandler()
        return handler.handle(args)
    except ImportError as e:
        print(f"Dependencies error: {e}")
        print("Please ensure you are running from the virtual environment and all requirements are installed.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())