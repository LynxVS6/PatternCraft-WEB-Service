def process_language_for_devicon(language):
    """Convert language names to devicon-compatible format."""
    language_map = {
        "c++": "cplusplus",
        "c#": "csharp",
        "csharp": "csharp",
        "cpp": "cplusplus",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "python": "python",
        "java": "java",
        "ruby": "ruby",
        "php": "php",
        "go": "go",
        "rust": "rust",
        "swift": "swift",
        "kotlin": "kotlin",
    }
    return language_map.get(language.lower(), language.lower())
