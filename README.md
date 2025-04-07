# 📋 GitHub Repository Clipboard Manager

_For when you get a brilliant coding idea in the bath and need to discuss it with an AI immediately (no judgment!)._

This project is a **web-based tool** designed to streamline interactions between **GitHub repositories** and **large language models (LLMs)** like ChatGPT, Claude, or Bard. The core purpose is to make it effortless to capture, format, and present code from repositories to LLMs for assistance or analysis.

Inspired by the command-line utility [`clip-files`](https://github.com/basnijholt/clip-files/), this tool provides a web interface for managing repository contexts. Read more about the workflow that led to these tools in [this blog post](https://www.nijho.lt/post/using-llms/).

## ✨ Core Functionality

The **GitHub Repository Clipboard Manager**:

1.  🔄 Maintains local clones of specified GitHub repositories, always **updated to their latest state**.
2.  🖱️ Allows selection of specific **file patterns or collections** via a simple web interface.
3.  📄 Automatically **formats repository content** with proper file paths and structure for optimal LLM understanding.
4.  📋 **Copies the formatted content** directly to your clipboard, ready to paste into any LLM interface.
5.  🪙 **Tracks token usage** to help manage context limits in LLM conversations.
6.  🌿 Supports switching between **different branches** of repositories.
7.  ➕ Enables **quick addition** of new repositories and file patterns.

## 🤔 Why Use This Tool?

-   **Save Time:** Eliminate the tedious manual process of selecting, copying, and formatting code for LLMs.
-   **Stay Current:** Always work with the latest version of your code from your repositories.
-   **Improve LLM Understanding:** Provide contextually accurate and well-structured code snippets to your AI assistant.
-   **Boost Productivity AFK:** Capture and share code context easily, even when away from your desk.
-   **Manage Context:** Keep track of token counts to stay within LLM limits.

## 🚀 Use Case

When working with code projects, developers often need to share portions of their codebase with **LLMs** to get assistance with debugging, refactoring, understanding patterns, or generating documentation. This tool streamlines that workflow significantly.

For example, you can define patterns like `"Core + Docs"` for a repository (including essential implementation files and documentation) or `"Configuration Files"` (gathering all settings files). With a **single click**, these are properly formatted, labeled with file paths, and copied to your clipboard – ready to paste into your preferred LLM.

Furthermore, this tool is invaluable for capturing code context for discussion with an AI when away from your main workstation. If you have an idea while **away from the keyboard (AFK)** - perhaps in bed, at the gym, or anywhere else - you can easily grab the pre-formatted codebase context from this tool via its web interface on any device and share it with your AI assistant.

The tool ensures that the content is always from the **latest version** of your code, properly **structured** for the LLM to understand the relationships between files, and **optimized for token efficiency**.
