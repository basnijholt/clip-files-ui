"""Main application for the GitHub Repository Clipboard Manager."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from typing import Annotated, Any

import yaml
from clip_files import generate_combined_content_with_specific_files
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global variables
GIT_EXECUTABLE = "/opt/homebrew/bin/git"  # Path to the git executable

app = FastAPI(title="GitHub Repository Clipboard Manager")
"""FastAPI application instance."""

# Directory to store the repositories
REPOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repos")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# Create repos directory if it doesn't exist
os.makedirs(REPOS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


# Models
class RepoConfig(BaseModel):
    """Configuration for a single repository."""

    name: str
    url: str
    branch: str = "main"
    patterns: dict[str, list[str]]


class Config(BaseModel):
    """Overall configuration containing a list of repositories."""

    repositories: list[RepoConfig]


# Load configuration
def load_config() -> Config:
    """Load configuration from the YAML file or create a default one."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config_data = yaml.safe_load(f)
                if config_data is None:
                    msg = "Configuration file is empty. Please populate it based on config.example.yaml."
                    raise ValueError(msg)  # noqa: TRY301
                return Config(**config_data)
        else:
            msg = (
                f"Configuration file {CONFIG_FILE} not found. "
                f"Please create it based on config.example.yaml."
            )
            raise FileNotFoundError(msg)  # noqa: TRY301
    except Exception:
        logger.exception("Error loading configuration")
        raise


# Save configuration
def save_config(config: Config) -> None:
    """Save the current configuration to the YAML file."""
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(json.loads(config.json()), f)


# Clone or update repository
def update_repository(repo_name: str, repo_url: str, branch: str = "main") -> bool:
    """Clone a repository if it doesn't exist, or update it if it does."""
    repo_path = os.path.join(REPOS_DIR, repo_name)

    try:
        if os.path.exists(repo_path):
            # Update existing repository
            logger.info("Updating repository: %s", repo_name)
            subprocess.run([GIT_EXECUTABLE, "-C", repo_path, "fetch", "--all"], check=True)
            subprocess.run(
                [GIT_EXECUTABLE, "-C", repo_path, "checkout", branch],
                check=True,
            )
            subprocess.run(
                [GIT_EXECUTABLE, "-C", repo_path, "reset", "--hard", f"origin/{branch}"],
                check=True,
            )
            subprocess.run(
                [GIT_EXECUTABLE, "-C", repo_path, "pull", "origin", branch],
                check=True,
            )
            return True
        # Clone repository
        logger.info("Cloning repository: %s from %s", repo_name, repo_url)
        subprocess.run(
            [GIT_EXECUTABLE, "clone", "--branch", branch, repo_url, repo_path],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        logger.exception("Git operation failed")
        return False


# Run clip-files on specific patterns
def run_clip_files(repo_name: str, patterns: list[str]) -> dict[str, Any]:
    """Run the clip-files logic on specified patterns within a repository."""
    repo_path = os.path.join(REPOS_DIR, repo_name)

    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")

    # Expand file globs within the repository
    expanded_files = []
    for pattern in patterns:
        if "*" in pattern:
            # Handle glob patterns
            import glob

            matches = glob.glob(os.path.join(repo_path, pattern))
            expanded_files.extend(matches)
        else:
            # Handle direct file paths
            filepath = os.path.join(repo_path, pattern)
            if os.path.exists(filepath):
                expanded_files.append(filepath)

    if not expanded_files:
        return {"success": False, "message": "No files matched the specified patterns"}

    try:
        # Create a temporary file to store output
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        # Run clip_files.py functionality directly
        content, tokens = generate_combined_content_with_specific_files(
            file_paths=expanded_files,
        )

        # Write to temp file (we'll read this back in JavaScript to copy to clipboard)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "message": f"Generated content with {tokens} tokens",
            "tokens": tokens,
            "temp_file": tmp_path,
            "content": content,
        }
    except Exception as e:
        logger.exception("Error running clip-files")
        return {"success": False, "message": f"Error: {e!s}"}


# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Serve the main HTML page."""
    config = load_config()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "config": config},
    )


@app.get("/api/repositories")
async def get_repositories() -> dict[str, Any]:
    """Get the list of configured repositories."""
    config = load_config()
    return {"repositories": config.repositories}


@app.post("/api/update_repository/{repo_name}")
async def update_repo_endpoint(
    repo_name: str,
    branch: str | None = None,
) -> dict[str, Any]:
    """Update a specific repository, optionally changing the branch."""
    config = load_config()

    repo = next((r for r in config.repositories if r.name == repo_name), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")

    # Update branch if provided
    if branch:
        repo.branch = branch
        save_config(config)

    success = update_repository(repo.name, repo.url, repo.branch)

    if success:
        return {"message": f"Repository {repo_name} updated successfully"}
    raise HTTPException(
        status_code=500,
        detail=f"Failed to update repository {repo_name}",
    )


@app.post("/api/run_clip_files/{repo_name}/{pattern_name}")
async def run_clip_files_endpoint(
    repo_name: str,
    pattern_name: str,
) -> dict[str, Any]:
    """Run clip-files for a specific repository and pattern name."""
    config = load_config()

    repo = next((r for r in config.repositories if r.name == repo_name), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")

    if pattern_name not in repo.patterns:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern {pattern_name} not found for repository {repo_name}",
        )

    patterns = repo.patterns[pattern_name]
    return run_clip_files(repo_name, patterns)


@app.post("/api/add_repository")
async def add_repository(
    name: Annotated[str, Form()],
    url: Annotated[str, Form()],
    branch: Annotated[str, Form()] = "main",
) -> dict[str, Any]:
    """Add a new repository to the configuration and clone it."""
    config = load_config()

    # Check if repository already exists
    if any(r.name == name for r in config.repositories):
        raise HTTPException(status_code=400, detail=f"Repository {name} already exists")

    # Add new repository
    new_repo = RepoConfig(name=name, url=url, branch=branch, patterns={})
    config.repositories.append(new_repo)
    save_config(config)

    # Clone the repository
    success = update_repository(name, url, branch)

    if success:
        return {"message": f"Repository {name} added successfully"}
    # Remove from config if cloning failed
    config.repositories = [r for r in config.repositories if r.name != name]
    save_config(config)
    raise HTTPException(
        status_code=500,
        detail=f"Failed to clone repository {name}",
    )


@app.post("/api/add_pattern")
async def add_pattern(
    repo_name: Annotated[str, Form()],
    pattern_name: Annotated[str, Form()],
    patterns: Annotated[str, Form()],
) -> dict[str, Any]:
    """Add a new pattern definition to a specific repository."""
    config = load_config()

    repo = next((r for r in config.repositories if r.name == repo_name), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")

    # Split patterns by comma or space
    pattern_list = [p.strip() for p in patterns.replace(",", " ").split() if p.strip()]

    # Add new pattern
    repo.patterns[pattern_name] = pattern_list
    save_config(config)

    return {"message": f"Pattern {pattern_name} added to {repo_name} successfully"}


@app.post("/api/update_branch/{repo_name}")
async def update_branch(
    repo_name: str,
    branch: Annotated[str, Form()],
) -> dict[str, Any]:
    """Update the branch for a specific repository."""
    config = load_config()

    repo = next((r for r in config.repositories if r.name == repo_name), None)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")

    repo.branch = branch
    save_config(config)

    # Update repository with new branch
    success = update_repository(repo.name, repo.url, branch)

    if success:
        return {"message": f"Branch for {repo_name} updated to {branch} successfully"}
    raise HTTPException(
        status_code=500,
        detail=f"Failed to update branch for {repo_name}",
    )


@app.on_event("startup")
async def startup_event() -> None:
    """Update all repositories on startup."""
    config = load_config()
    for repo in config.repositories:
        update_repository(repo.name, repo.url, repo.branch)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
