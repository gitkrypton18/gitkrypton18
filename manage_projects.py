#!/usr/bin/env python3
"""
manage_projects.py

CLI utility to add, remove, and dynamically sync GitHub repository details
into the README.md file.

Usage:
  python manage_projects.py add <owner/repo> [--deploy <url>] [--screenshot <url_or_path>]
  python manage_projects.py remove <owner/repo>
  python manage_projects.py sync [--dry-run]
"""

import os
import sys
import json
import urllib.request
import urllib.error
import re
import argparse

PROJECTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects.json")
README_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")

# Simple map of common technology names to Shields.io badges or text labels
TECH_BADGE_MAP = {
    "python": "https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white",
    "fastapi": "https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white",
    "react": "https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB",
    "pytorch": "https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white",
    "tensorflow": "https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white",
    "mongodb": "https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white",
    "docker": "https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white",
    "huggingface": "https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-yellow?style=flat-square",
    "javascript": "https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black",
    "typescript": "https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white",
    "nodejs": "https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white",
    "nextjs": "https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white",
    "css": "https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white",
    "html": "https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white",
    "streamlit": "https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white",
    "arduino": "https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white"
}

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {PROJECTS_FILE}: {e}")
        return []

def save_projects(projects):
    try:
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2)
        print(f"[ok] Saved configuration to {PROJECTS_FILE}")
    except Exception as e:
        print(f"Error saving {PROJECTS_FILE}: {e}")

def get_github_repo_data(repo_name):
    """Fetch repo details from GitHub API."""
    url = f"https://api.github.com/repos/{repo_name}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "gitkrypton18-profile-sync")
    
    # Use GITHUB_TOKEN if available to avoid rate limiting
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[warn] GitHub API error for {repo_name}: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"[warn] Network error fetching {repo_name}: {e}")
        return None

def build_tech_badge(topic):
    topic_lower = topic.lower().replace("-", "").replace("_", "")
    badge_url = TECH_BADGE_MAP.get(topic_lower)
    if badge_url:
        return f'<img src="{badge_url}" alt="{topic}" />'
    # Fallback to general shield for unknown tags
    clean_topic = topic.replace("-", " ").title()
    encoded_topic = urllib.parse.quote(clean_topic)
    return f'<img src="https://img.shields.io/badge/{encoded_topic}-555555?style=flat-square" alt="{topic}" />'

def generate_markdown(projects):
    lines = []
    lines.append('<!-- PROJECTS-START -->')
    lines.append('<!-- This section is dynamically updated by manage_projects.py. Do not edit directly. -->')
    lines.append('')
    lines.append('<div align="center">')
    lines.append('')
    
    for proj in projects:
        repo = proj["repo"]
        print(f"Syncing data for repository: {repo} ...")
        
        # Fetch data from GitHub API
        api_data = get_github_repo_data(repo)
        
        # Determine values with fallback
        display_name = repo.split("/")[-1]
        desc = proj.get("description")
        homepage = proj.get("deploy_url")
        topics = proj.get("tech_stack", [])
        
        if api_data:
            display_name = api_data.get("name", display_name)
            desc = desc or api_data.get("description", "No description provided.")
            homepage = homepage or api_data.get("homepage")
            if not topics and api_data.get("topics"):
                topics = api_data.get("topics")
        
        desc = desc or "Professional project description and implementation details."
        homepage = homepage or f"https://github.com/{repo}"
        
        # Format tech badges
        badges = " ".join(build_tech_badge(t) for t in topics) if topics else ""
        
        screenshot_html = ""
        if proj.get("screenshot_path"):
            screenshot_html = f'<img src="{proj["screenshot_path"]}" width="100%" style="border-radius: 8px; border: 1px solid #30363d; margin-top: 10px;" alt="{display_name} Dashboard" />'

        lines.append(f'### 🟢 [{display_name}](https://github.com/{repo})')
        lines.append('')
        lines.append(f'> {desc}')
        lines.append('')
        
        # Add badge list and Deploy Link
        deploy_btn = f' &nbsp;&nbsp;•&nbsp;&nbsp; <a href="{homepage}"><b>🚀 Live Demo</b></a>' if homepage else ""
        lines.append(f'<p align="left">{badges}{deploy_btn}</p>')
        
        if screenshot_html:
            lines.append(screenshot_html)
            
        lines.append('')
        lines.append('<hr style="height: 1px; background-color: #30363d; border: none; margin: 2rem 0;" />')
        lines.append('')
        
    # Remove the last horizontal rule
    if lines and lines[-1] == '':
        lines.pop()
    if lines and lines[-1].startswith('<hr'):
        lines.pop()
        
    lines.append('</div>')
    lines.append('<!-- PROJECTS-END -->')
    
    return "\n".join(lines)

def sync_readme(dry_run=False):
    projects = load_projects()
    if not projects:
        print("No projects configured in projects.json")
        return
        
    new_section = generate_markdown(projects)
    
    if dry_run:
        print("\n--- Dry Run Output ---")
        print(new_section)
        print("----------------------\n")
        return

    if not os.path.exists(README_FILE):
        print(f"README.md not found at {README_FILE}")
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!--\s*PROJECTS-START\s*-->.*?<!--\s*PROJECTS-END\s*-->"
    if not re.search(pattern, content, re.DOTALL):
        print("[warn] Placeholders <!-- PROJECTS-START --> and <!-- PROJECTS-END --> not found in README.md.")
        print("Appending to the end of the file instead.")
        new_content = content + "\n\n" + new_section
    else:
        new_content = re.sub(pattern, new_section, content, flags=re.DOTALL)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("[ok] README.md has been successfully updated with project list.")

def main():
    parser = argparse.ArgumentParser(description="Manage Featured Projects in README.md")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new project")
    parser_add.add_argument("repo", help="GitHub repo format: owner/repo")
    parser_add.add_argument("--deploy", help="URL of deployed project")
    parser_add.add_argument("--screenshot", help="URL or path to screenshot")
    parser_add.add_argument("--desc", help="Optional override description")
    parser_add.add_argument("--stack", nargs="+", help="Optional tech stack topics")

    # Remove command
    parser_remove = subparsers.add_parser("remove", help="Remove an existing project")
    parser_remove.add_argument("repo", help="GitHub repo format: owner/repo")

    # Sync command
    parser_sync = subparsers.add_parser("sync", help="Sync projects to README.md")
    parser_sync.add_argument("--dry-run", action="store_true", help="Print result without writing")

    args = parser.parse_args()

    if args.command == "add":
        projects = load_projects()
        # Check if already exists
        exists = False
        for p in projects:
            if p["repo"].lower() == args.repo.lower():
                # Update details
                if args.deploy: p["deploy_url"] = args.deploy
                if args.screenshot: p["screenshot_path"] = args.screenshot
                if args.desc: p["description"] = args.desc
                if args.stack: p["tech_stack"] = args.stack
                exists = True
                print(f"Updated config for {args.repo}")
                break
        
        if not exists:
            new_proj = {
                "repo": args.repo,
                "deploy_url": args.deploy or "",
                "screenshot_path": args.screenshot or ""
            }
            if args.desc:
                new_proj["description"] = args.desc
            if args.stack:
                new_proj["tech_stack"] = args.stack
            projects.append(new_proj)
            print(f"Added config for {args.repo}")
            
        save_projects(projects)
        # Auto-sync
        sync_readme()

    elif args.command == "remove":
        projects = load_projects()
        filtered = [p for p in projects if p["repo"].lower() != args.repo.lower()]
        if len(filtered) == len(projects):
            print(f"Project {args.repo} not found in config.")
        else:
            save_projects(filtered)
            sync_readme()

    elif args.command == "sync" or not args.command:
        sync_readme(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
