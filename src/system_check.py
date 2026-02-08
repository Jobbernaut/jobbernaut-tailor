"""
System requirements verification for the resume optimization pipeline.
Checks all dependencies before pipeline execution to prevent runtime failures.
"""

import os
import sys
import shutil
import platform
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class SystemRequirements:
    """Verify system requirements and dependencies."""
    
    def __init__(self, config: dict = None):
        """
        Initialize system requirements checker.
        
        Args:
            config: Optional configuration dict with system_requirements settings
        """
        self.console = Console()
        self.config = config or {}
        self.system_config = self.config.get("system_requirements", {})
        self.check_on_startup = self.system_config.get("check_on_startup", True)
        self.allow_missing_optional = self.system_config.get("allow_missing_optional", False)
        
        # Track check results
        self.checks_passed: List[Tuple[str, str]] = []
        self.checks_failed: List[Tuple[str, str, str]] = []  # (name, error, fix)
        self.checks_warning: List[Tuple[str, str, str]] = []  # (name, warning, fix)
    
    def check_python_version(self) -> bool:
        """Check if Python version is 3.8 or higher."""
        version = sys.version_info
        required_major = 3
        required_minor = 8
        
        if (version.major, version.minor) >= (required_major, required_minor):
            self.checks_passed.append(
                ("Python Version", f"{version.major}.{version.minor}.{version.micro}")
            )
            return True
        else:
            self.checks_failed.append((
                "Python Version",
                f"Python {version.major}.{version.minor} found, but {required_major}.{required_minor}+ required",
                f"Install Python {required_major}.{required_minor} or higher from https://www.python.org/downloads/"
            ))
            return False
    
    def check_python_packages(self) -> bool:
        """Check if all required Python packages are installed."""
        try:
            # Read requirements.txt
            if not os.path.exists("requirements.txt"):
                self.checks_failed.append((
                    "Python Packages",
                    "requirements.txt not found",
                    "Ensure requirements.txt exists in the project root"
                ))
                return False
            
            # Read with explicit UTF-8 encoding and error handling for robustness
            with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            # Try importing key packages
            missing_packages = []
            key_packages = [
                "fastapi_poe",
                "pydantic",
                "yaml",
                "jinja2",
                "rich",
                "dotenv"
            ]
            
            for package in key_packages:
                try:
                    if package == "yaml":
                        __import__("yaml")
                    elif package == "dotenv":
                        __import__("dotenv")
                    else:
                        __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                self.checks_failed.append((
                    "Python Packages",
                    f"Missing packages: {', '.join(missing_packages)}",
                    "Run: pip install -r requirements.txt"
                ))
                return False
            else:
                self.checks_passed.append(
                    ("Python Packages", f"{len(key_packages)} key packages verified")
                )
                return True
                
        except Exception as e:
            self.checks_failed.append((
                "Python Packages",
                f"Error checking packages: {str(e)}",
                "Run: pip install -r requirements.txt"
            ))
            return False
    
    def check_pdflatex(self) -> bool:
        """Check if pdflatex is installed and accessible."""
        pdflatex_path = shutil.which("pdflatex")
        
        if pdflatex_path:
            self.checks_passed.append(
                ("pdflatex", f"Found at {pdflatex_path}")
            )
            return True
        else:
            system = platform.system()
            
            if system == "Windows":
                fix_msg = (
                    "Install MiKTeX from https://miktex.org/download\n"
                    "   After installation, restart your terminal/IDE"
                )
            elif system == "Darwin":  # macOS
                fix_msg = (
                    "Install MacTeX from https://www.tug.org/mactex/\n"
                    "   Or use Homebrew: brew install --cask mactex-no-gui"
                )
            else:  # Linux
                fix_msg = (
                    "Install TeX Live:\n"
                    "   Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-extra\n"
                    "   Fedora: sudo dnf install texlive-scheme-basic\n"
                    "   Arch: sudo pacman -S texlive-core"
                )
            
            self.checks_failed.append((
                "pdflatex",
                "pdflatex not found in system PATH",
                fix_msg
            ))
            return False
    
    def check_latex_classes(self) -> bool:
        """Check if required LaTeX class files exist."""
        required_classes = [
            "latex/resume.cls",
            "latex/coverletter.cls"
        ]
        
        missing_classes = []
        for cls_file in required_classes:
            if not os.path.exists(cls_file):
                missing_classes.append(cls_file)
        
        if missing_classes:
            self.checks_failed.append((
                "LaTeX Classes",
                f"Missing class files: {', '.join(missing_classes)}",
                "Ensure latex/resume.cls and latex/coverletter.cls exist in the project"
            ))
            return False
        else:
            self.checks_passed.append(
                ("LaTeX Classes", "resume.cls, coverletter.cls found")
            )
            return True
    
    def check_directories(self) -> bool:
        """Check if required directories exist."""
        required_dirs = [
            "prompts",
            "latex",
            "profile",
            "data",
            "templates"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.isdir(dir_path):
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.checks_failed.append((
                "Project Directories",
                f"Missing directories: {', '.join(missing_dirs)}",
                "Create missing directories or restore from project template"
            ))
            return False
        else:
            self.checks_passed.append(
                ("Project Directories", f"{len(required_dirs)} directories verified")
            )
            return True
    
    def check_config_files(self) -> bool:
        """Check if required configuration files exist."""
        required_files = [
            ("config.json", "Configuration file"),
            (".env", "Environment variables (contains POE_API_KEY)")
        ]
        
        missing_files = []
        for file_path, description in required_files:
            if not os.path.exists(file_path):
                missing_files.append(f"{file_path} ({description})")
        
        if missing_files:
            self.checks_failed.append((
                "Configuration Files",
                f"Missing files: {', '.join(missing_files)}",
                "Create .env with POE_API_KEY and ensure config.json exists"
            ))
            return False
        else:
            self.checks_passed.append(
                ("Configuration Files", "config.json, .env found")
            )
            return True
    
    def check_api_key(self) -> bool:
        """Check if POE_API_KEY is set in environment."""
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("POE_API_KEY")
        
        if api_key and len(api_key) > 0:
            # Mask the key for display
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            self.checks_passed.append(
                ("POE API Key", f"Set ({masked_key})")
            )
            return True
        else:
            self.checks_failed.append((
                "POE API Key",
                "POE_API_KEY not found in .env file",
                "Add POE_API_KEY=your_key_here to .env file"
            ))
            return False
    
    def check_optional_files(self) -> bool:
        """Check optional files and warn if missing."""
        optional_files = [
            ("profile/master_resume.json", "Master resume data"),
            ("profile/referral_contact.json", "Referral contact info (optional)"),
            ("data/applications.yaml", "Job applications list")
        ]
        
        missing_optional = []
        for file_path, description in optional_files:
            if not os.path.exists(file_path):
                missing_optional.append(f"{file_path} ({description})")
        
        if missing_optional:
            self.checks_warning.append((
                "Optional Files",
                f"Missing: {', '.join(missing_optional)}",
                "These files are needed for pipeline execution but not for system verification"
            ))
            return False
        else:
            self.checks_passed.append(
                ("Optional Files", "All optional files present")
            )
            return True
    
    def run_all_checks(self) -> bool:
        """
        Run all system requirement checks.
        
        Returns:
            True if all critical checks pass, False otherwise
        """
        self.console.print("\n[bold cyan]System Requirements Verification[/bold cyan]")
        self.console.print("=" * 60 + "\n")
        
        # Run all checks
        checks = [
            ("Python Version", self.check_python_version),
            ("Python Packages", self.check_python_packages),
            ("pdflatex", self.check_pdflatex),
            ("LaTeX Classes", self.check_latex_classes),
            ("Project Directories", self.check_directories),
            ("Configuration Files", self.check_config_files),
            ("POE API Key", self.check_api_key),
            ("Optional Files", self.check_optional_files)
        ]
        
        for check_name, check_func in checks:
            try:
                check_func()
            except Exception as e:
                self.checks_failed.append((
                    check_name,
                    f"Check failed with error: {str(e)}",
                    "Review the error and ensure all dependencies are properly installed"
                ))
        
        # Display results
        self._display_results()
        
        # Determine if we can proceed
        has_critical_failures = len(self.checks_failed) > 0
        
        if has_critical_failures:
            return False
        elif len(self.checks_warning) > 0 and not self.allow_missing_optional:
            self.console.print("\n[yellow]⚠️  Warnings detected. Pipeline may fail during execution.[/yellow]")
            return True  # Allow to proceed but with warnings
        else:
            self.console.print("\n[green]✅ All system requirements verified![/green]")
            return True
    
    def _display_results(self) -> None:
        """Display check results in a formatted table."""
        # Create results table
        table = Table(title="Verification Results", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Status", width=15)
        table.add_column("Details", width=40)
        
        # Add passed checks
        for name, details in self.checks_passed:
            table.add_row(name, "[green]✓ PASS[/green]", details)
        
        # Add warnings
        for name, warning, _ in self.checks_warning:
            table.add_row(name, "[yellow]⚠ WARN[/yellow]", warning)
        
        # Add failed checks
        for name, error, _ in self.checks_failed:
            table.add_row(name, "[red]✗ FAIL[/red]", error)
        
        self.console.print(table)
        
        # Display detailed fix instructions for failures
        if self.checks_failed:
            self.console.print("\n[bold red]❌ Critical Issues Found[/bold red]")
            self.console.print("=" * 60)
            
            for i, (name, error, fix) in enumerate(self.checks_failed, 1):
                panel = Panel(
                    f"[red]Error:[/red] {error}\n\n[cyan]Fix:[/cyan]\n{fix}",
                    title=f"{i}. {name}",
                    border_style="red"
                )
                self.console.print(panel)
            
            self.console.print("\n[bold red]Pipeline cannot start until these issues are resolved.[/bold red]\n")
        
        # Display warnings
        if self.checks_warning:
            self.console.print("\n[bold yellow]⚠️  Warnings[/bold yellow]")
            self.console.print("=" * 60)
            
            for i, (name, warning, fix) in enumerate(self.checks_warning, 1):
                self.console.print(f"\n{i}. [yellow]{name}:[/yellow] {warning}")
                self.console.print(f"   [dim]{fix}[/dim]")
            
            self.console.print()


def verify_system_requirements(config: dict = None) -> bool:
    """
    Convenience function to verify system requirements.
    
    Args:
        config: Optional configuration dict
        
    Returns:
        True if all critical requirements are met, False otherwise
    """
    checker = SystemRequirements(config)
    return checker.run_all_checks()
