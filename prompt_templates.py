"""Utilities for loading and rendering AI prompt templates."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@dataclass(frozen=True)
class PromptTemplate:
    """Structured prompt template with lightweight frontmatter metadata."""

    metadata: dict[str, object]
    content: str

    def render(self, **context):
        return self.content.format(**context)


def _coerce_metadata_value(value):
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in {"\"", "'"}
    ):
        return value[1:-1]

    return value


def _parse_prompt_file(raw_text):
    if not raw_text.startswith("---\n"):
        return PromptTemplate(metadata={}, content=raw_text.strip())

    lines = raw_text.splitlines()
    metadata = {}

    for index in range(1, len(lines)):
        line = lines[index]
        if line == "---":
            body = "\n".join(lines[index + 1:]).strip()
            return PromptTemplate(metadata=metadata, content=body)

        if not line.strip():
            continue

        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid prompt frontmatter line: {line}")

        metadata[key.strip()] = _coerce_metadata_value(value.strip())

    raise ValueError("Prompt frontmatter is missing a closing '---' delimiter")


@lru_cache(maxsize=None)
def load_prompt_template(relative_path):
    """Load a prompt template from the prompts directory."""
    template_path = PROMPTS_DIR / relative_path
    raw_text = template_path.read_text(encoding="utf-8")
    return _parse_prompt_file(raw_text)


def load_prompt_text(relative_path):
    """Load only the prompt body text."""
    return load_prompt_template(relative_path).content


def render_prompt_template(relative_path, **context):
    """Render a prompt template with the supplied string context."""
    return load_prompt_template(relative_path).render(**context)