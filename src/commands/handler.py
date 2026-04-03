import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from ..core.repository import Repository
from ..core.differ import Differ
from ..core.models import Changelist

console = Console()

class CommandHandler:
    def __init__(self):
        self.repo = Repository()
        
    def handle(self, args):
        cmd = args.command
        if not cmd:
            console.print("[red]No command provided.[/red]")
            return 1
            
        try:
            if cmd == "init": self.init(args)
            elif cmd == "status": self.status(args)
            elif cmd == "diff": self.diff(args)
            elif cmd == "save": self.save(args)
            elif cmd == "list": self.list_cl(args)
            elif cmd == "show": self.show(args)
            else:
                console.print(f"[yellow]Command '{cmd}' is a stub and not fully implemented yet.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Execution Error:[/bold red] {e}")
            return 1
        return 0

    def init(self, args):
        if self.repo.initialize():
            differ = Differ(self.repo)
            # Create the initial snapshot
            tracked = differ.get_tracked_files()
            differ.snapshot_to_state(tracked)
            console.print("[green]Successfully initialized ai-changelist repository![/green]")
        else:
            console.print("[yellow]Repository already initialized.[/yellow]")
            
    def status(self, args):
        if not self.repo.is_initialized:
            console.print("[red]Not initialized. Run 'ai-cl init' first.[/red]")
            return
            
        differ = Differ(self.repo)
        changes = differ.get_status()
        
        if not changes:
            console.print("[green]No changes detected relative to HEAD.[/green]")
            return
            
        console.print("\n[bold]Changes relative to last save:[/bold]")
        for c in changes:
            color = "green" if c.action.value == "create" else ("red" if c.action.value == "delete" else "yellow")
            console.print(f"[{color}]{c.action.value.upper():<8}[/{color}] {c.path}")
        console.print("")

    def save(self, args):
        if not self.repo.is_initialized:
            console.print("[red]Not initialized. Run 'ai-cl init' first.[/red]")
            return
            
        prompt = args.prompt
        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    prompt = f.read()
            except Exception as e:
                console.print(f"[red]Error reading prompt file: {e}[/red]")
                return
                
        differ = Differ(self.repo)
        changes = differ.get_status()
        
        if not changes:
            console.print("[yellow]No changes to save![/yellow]")
            return
            
        cl = Changelist(
            prompt=prompt,
            branch=self.repo.get_current_branch(),
            parent_id=self.repo.get_head_id(),
            files_changed=changes
        )
        
        self.repo.save_changelist(cl)
        self.repo.update_head(branch=cl.branch, current_id=cl.id)
        differ.sync_state(changes)
        
        console.print(f"[green]Saved changelist {cl.id}[/green]")
        console.print(f"Recorded {len(changes)} file changes.")
        
    def list_cl(self, args):
        if not self.repo.is_initialized:
            console.print("[red]Not initialized.[/red]")
            return
            
        cls = self.repo.get_all_changelists()
        if not cls:
            console.print("No changelists found in history.")
            return
            
        table = Table(title="AI Changelist History")
        table.add_column("ID", style="cyan")
        table.add_column("Branch", style="magenta")
        table.add_column("Time", style="blue")
        table.add_column("Prompt / Summary")
        
        for cl in cls[:args.limit if args.limit else None]:
            snippet = (cl.prompt[:40] + "...") if cl.prompt and len(cl.prompt) > 40 else (cl.prompt or "")
            if not snippet:
                snippet = f"[{len(cl.files_changed)} files changed]"
                
            # Star the current HEAD
            is_head = " *" if cl.id == self.repo.get_head_id() else ""
            table.add_row(cl.id[:8] + is_head, cl.branch, cl.timestamp[:19].replace("T", " "), snippet)
            
        console.print(table)

    def show(self, args):
        if not self.repo.is_initialized:
            console.print("[red]Not initialized.[/red]")
            return
        
        # Fast lookup handling for short UUIDs by scanning if not full UUID
        cl = self.repo.get_changelist(args.id)
        if not cl:
            # Fallback search by prefix
            all_objs = self.repo.get_all_changelists()
            matches = [obj for obj in all_objs if obj.id.startswith(args.id)]
            if len(matches) == 1:
                cl = matches[0]
            elif len(matches) > 1:
                console.print(f"[red]Ambiguous ID: {args.id} matches multiple changelists.[/red]")
                return
            else:
                console.print(f"[red]Changelist {args.id} not found.[/red]")
                return
            
        console.print(f"\n[bold cyan]Changelist:[/bold cyan] {cl.id}")
        console.print(f"[bold cyan]Branch:[/bold cyan]     {cl.branch}")
        console.print(f"[bold cyan]Date:[/bold cyan]       {cl.timestamp}")
        console.print(f"[bold cyan]Parent:[/bold cyan]     {cl.parent_id or 'None (Root)'}")
        
        if cl.prompt:
            console.print(Panel(cl.prompt, title="Original Prompt", border_style="green"))
            
        console.print(f"\n[bold]{len(cl.files_changed)} File(s) Changed:[/bold]\n")
        for fc in cl.files_changed:
            color = "green" if fc.action.value == "create" else ("red" if fc.action.value == "delete" else "yellow")
            console.print(f"[{color}]{fc.action.value.upper():<8}[/{color}] {fc.path}")
            if fc.diff:
                syntax = Syntax(fc.diff, "diff", theme="monokai", line_numbers=False)
                console.print(syntax)
                
    def diff(self, args):
        if not self.repo.is_initialized:
            console.print("[red]Not initialized.[/red]")
            return
            
        if args.id:
            console.print("[yellow]Diffing against a specific historical ID is not implemented yet. Showing uncommitted changes vs HEAD.[/yellow]")
            
        differ = Differ(self.repo)
        changes = differ.get_status()
        
        if not changes:
            console.print("[green]No changes detected.[/green]")
            return
            
        for fc in changes:
            console.print(f"\n[bold cyan]{fc.path}[/bold cyan] ({fc.action.value})")
            if fc.diff:
                syntax = Syntax(fc.diff, "diff", theme="monokai", line_numbers=False)
                console.print(syntax)
