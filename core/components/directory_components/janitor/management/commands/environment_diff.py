from directory_components.janitor.management.commands.vault_diff import Command

# `environment_diff` was renamed to `vault_diff`. Improting here to maintain backwards compatibility.

__all__ = ['Command']
