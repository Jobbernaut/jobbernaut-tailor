"""
Real-time progress tracking with shadow failure visibility for the job application pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table


@dataclass
class StepRetryInfo:
    """Track retry information for a specific step."""
    step_name: str
    total_attempts: int = 0
    failures: List[str] = field(default_factory=list)  # List of failure reasons


@dataclass
class JobProgress:
    """Track progress for a single job with shadow failure tracking."""
    job_id: str
    job_title: str
    company_name: str
    current_step: int
    total_steps: int
    status: str  # 'running', 'completed', 'failed'
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Shadow failure tracking
    total_retries: int = 0  # Total retries across all steps
    retry_by_step: Dict[str, StepRetryInfo] = field(default_factory=dict)
    api_call_retries: int = 0  # Retries due to API failures
    validation_retries: int = 0  # Retries due to validation failures
    quality_retries: int = 0  # Retries due to quality issues


class ProgressTracker:
    """Real-time progress tracking with shadow failure visibility."""
    
    PIPELINE_STEPS = [
        "Job Resonance Analysis",
        "Company Research", 
        "Storytelling Arc",
        "Resume Generation",
        "Cover Letter Generation",
        "Resume LaTeX Rendering",
        "Cover Letter LaTeX Rendering",
        "Resume PDF Compilation",
        "Cover Letter PDF Compilation",
        "Referral Resume",
        "Referral Cover Letter",
        "Cleanup"
    ]
    
    def __init__(self, total_jobs: int):
        """
        Initialize the progress tracker.
        
        Args:
            total_jobs: Total number of jobs to process
        """
        self.total_jobs = total_jobs
        self.jobs: Dict[str, JobProgress] = {}
        self.console = Console()
        
    def add_job(self, job_id: str, job_title: str, company_name: str):
        """
        Register a new job for tracking.
        
        Args:
            job_id: Unique job identifier
            job_title: Job title
            company_name: Company name
        """
        self.jobs[job_id] = JobProgress(
            job_id=job_id,
            job_title=job_title,
            company_name=company_name,
            current_step=0,
            total_steps=len(self.PIPELINE_STEPS),
            status='running',
            start_time=datetime.now()
        )
    
    def update_step(self, job_id: str, step_index: int, step_name: str = None):
        """
        Update the current step for a job.
        
        Args:
            job_id: Job identifier
            step_index: Index of the current step (0-based)
            step_name: Optional step name (for validation)
        """
        if job_id not in self.jobs:
            return
        
        self.jobs[job_id].current_step = step_index
    
    def record_retry(self, job_id: str, step_name: str, failure_reason: str, retry_type: str = "validation"):
        """
        Record a retry attempt (shadow failure).
        
        Args:
            job_id: Job identifier
            step_name: Name of the step where retry occurred
            failure_reason: Why the retry was needed
            retry_type: Type of retry ('api', 'validation', 'quality')
        """
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        
        # Increment total retries
        job.total_retries += 1
        
        # Track by retry type
        if retry_type == "api":
            job.api_call_retries += 1
        elif retry_type == "validation":
            job.validation_retries += 1
        elif retry_type == "quality":
            job.quality_retries += 1
        
        # Track by step
        if step_name not in job.retry_by_step:
            job.retry_by_step[step_name] = StepRetryInfo(step_name=step_name)
        
        step_info = job.retry_by_step[step_name]
        step_info.total_attempts += 1
        step_info.failures.append(failure_reason)
    
    def mark_completed(self, job_id: str):
        """
        Mark a job as completed.
        
        Args:
            job_id: Job identifier
        """
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        job.status = 'completed'
        job.end_time = datetime.now()
        job.current_step = job.total_steps
    
    def mark_failed(self, job_id: str, error_message: str):
        """
        Mark a job as failed.
        
        Args:
            job_id: Job identifier
            error_message: Error message describing the failure
        """
        if job_id not in self.jobs:
            return
        
        job = self.jobs[job_id]
        job.status = 'failed'
        job.error = error_message
        job.end_time = datetime.now()
    
    def generate_table(self) -> Table:
        """
        Generate a rich Table showing current progress with shadow failures.
        
        Returns:
            Rich Table object for display
        """
        table = Table(title="Job Processing Progress", show_header=True, header_style="bold magenta")
        
        table.add_column("Job", style="cyan", width=25, no_wrap=True)
        table.add_column("Company", style="magenta", width=15, no_wrap=True)
        table.add_column("Progress", width=25)
        table.add_column("Status", width=20, no_wrap=True)
        table.add_column("Retries", style="yellow", width=10, justify="right")
        
        for job in self.jobs.values():
            # Truncate long titles
            title = job.job_title[:22] + "..." if len(job.job_title) > 25 else job.job_title
            company = job.company_name[:12] + "..." if len(job.company_name) > 15 else job.company_name
            
            # Progress bar
            progress_pct = (job.current_step / job.total_steps) * 100
            bar_length = 20
            filled = int(progress_pct / 5)
            progress_bar = f"[{'█' * filled}{' ' * (bar_length - filled)}] {progress_pct:.0f}%"
            
            # Status with color
            if job.status == 'completed':
                status = "[green]✓ Complete[/green]"
            elif job.status == 'failed':
                status = f"[red]✗ Failed[/red]"
            else:
                current_step_name = self.PIPELINE_STEPS[job.current_step] if job.current_step < len(self.PIPELINE_STEPS) else "Finalizing"
                # Truncate step name for display
                step_display = current_step_name[:15] + "..." if len(current_step_name) > 18 else current_step_name
                status = f"[yellow]⟳ {step_display}[/yellow]"
            
            # Retry count with color coding
            if job.total_retries == 0:
                retry_display = "[green]0[/green]"
            elif job.total_retries <= 2:
                retry_display = f"[yellow]{job.total_retries}[/yellow]"
            else:
                retry_display = f"[red]{job.total_retries}[/red]"
            
            table.add_row(title, company, progress_bar, status, retry_display)
        
        return table
    
    def get_summary(self) -> str:
        """
        Get summary statistics including shadow failures.
        
        Returns:
            Summary string with job counts and retry statistics
        """
        completed = sum(1 for j in self.jobs.values() if j.status == 'completed')
        failed = sum(1 for j in self.jobs.values() if j.status == 'failed')
        running = sum(1 for j in self.jobs.values() if j.status == 'running')
        
        total_retries = sum(j.total_retries for j in self.jobs.values())
        total_api_retries = sum(j.api_call_retries for j in self.jobs.values())
        total_validation_retries = sum(j.validation_retries for j in self.jobs.values())
        total_quality_retries = sum(j.quality_retries for j in self.jobs.values())
        
        summary_lines = [
            f"\nTotal: {self.total_jobs} | ✓ {completed} | ✗ {failed} | ⟳ {running}",
            f"Shadow Failures: {total_retries} total ({total_api_retries} API, {total_validation_retries} validation, {total_quality_retries} quality)"
        ]
        
        return "\n".join(summary_lines)
    
    def generate_detailed_report(self) -> str:
        """
        Generate detailed shadow failure report for post-processing analysis.
        
        Returns:
            Detailed report string with per-job retry breakdown
        """
        lines = [
            "=" * 80,
            "SHADOW FAILURE DETAILED REPORT",
            "=" * 80,
            ""
        ]
        
        jobs_with_retries = [j for j in self.jobs.values() if j.total_retries > 0]
        
        if not jobs_with_retries:
            lines.append("No shadow failures detected! All jobs processed without retries.")
            lines.append("")
        else:
            for job in jobs_with_retries:
                lines.append(f"Job: {job.job_title} at {job.company_name}")
                lines.append(f"  Job ID: {job.job_id}")
                lines.append(f"  Total Retries: {job.total_retries}")
                lines.append(f"  Breakdown: {job.api_call_retries} API, {job.validation_retries} validation, {job.quality_retries} quality")
                
                if job.retry_by_step:
                    lines.append(f"  Retries by Step:")
                    for step_name, step_info in job.retry_by_step.items():
                        lines.append(f"    - {step_name}: {step_info.total_attempts} retries")
                        for i, failure in enumerate(step_info.failures, 1):
                            # Truncate long failure messages
                            failure_msg = failure[:70] + "..." if len(failure) > 70 else failure
                            lines.append(f"      {i}. {failure_msg}")
                
                lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
