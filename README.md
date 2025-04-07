# GitHub Repository Clipboard Manager - Project Description

This project is a web-based tool designed to streamline interactions between GitHub repositories and large language models (LLMs) like ChatGPT, Claude, or Bard. The core purpose is to make it effortless to capture, format, and present code from repositories to LLMs for assistance or analysis.

## Core Functionality

The GitHub Repository Clipboard Manager:

1. Maintains local clones of specified GitHub repositories, always updated to their latest state
2. Allows selection of specific file patterns or collections via a simple web interface
3. Automatically formats repository content with proper file paths and structure for optimal LLM understanding
4. Copies the formatted content directly to your clipboard, ready to paste into any LLM interface
5. Tracks token usage to help manage context limits in LLM conversations
6. Supports switching between different branches of repositories
7. Enables quick addition of new repositories and file patterns

## Use Case

When working with code projects, developers often need to share portions of their codebase with LLMs to get assistance with debugging, refactoring, understanding patterns, or generating documentation. This tool eliminates the tedious process of manually selecting, copying, and formatting files for LLM consumption.

For example, you can define patterns like "Core + Docs" for a repository that includes essential implementation files and documentation, or "Configuration Files" that gathers all settings files. With a single click, these are properly formatted, labeled with file paths, and copied to your clipboard - ready to paste into your preferred LLM.

The tool ensures that the content is always from the latest version of your code, properly structured for the LLM to understand the relationships between files, and optimized for token efficiency.
