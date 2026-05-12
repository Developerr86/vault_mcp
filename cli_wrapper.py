"""
CLI Wrapper for Vault 78 MCP Server.

Spawns subprocesses to execute CLI commands against the Obsidian vault.
All user-supplied arguments are passed as safe argument lists — never via shell.
"""

import asyncio
import os
import shlex
from pathlib import Path
from typing import Optional


class CliWrapper:
    """Async wrapper around a vault CLI tool with strict path validation.

    Detects the CLI tool type from OBSIDIAN_CLI_COMMAND and builds
    appropriate argument lists for each operation.
    """

    def __init__(self) -> None:
        path_str = os.getenv("VAULT_ABSOLUTE_PATH")
        if not path_str:
            raise RuntimeError("VAULT_ABSOLUTE_PATH environment variable is not set")
        self.vault_path = Path(path_str).resolve()

        cmd = os.getenv("OBSIDIAN_CLI_COMMAND", "")
        if not cmd:
            raise RuntimeError("OBSIDIAN_CLI_COMMAND environment variable is not set")
        self.cli_args = shlex.split(cmd)
        self.exe_name = Path(self.cli_args[0]).stem.lower()

        self._is_powershell = "powershell" in self.exe_name
        self._is_grep = self.exe_name in ("rg", "grep", "findstr")

    # ── Security helpers ───────────────────────────────────────────────

    def _safe_resolve(self, rel_path: str, *, allow_dir: bool = False) -> Path:
        """Resolve a relative path against vault root and prevent traversal."""
        resolved = (self.vault_path / rel_path).resolve()
        try:
            resolved.relative_to(self.vault_path)
        except ValueError:
            raise PermissionError(
                f"Directory traversal blocked: '{rel_path}' resolves outside the vault"
            )
        suffix = resolved.suffix.lower()
        if not allow_dir and suffix not in (".md", ".canvas"):
            raise ValueError(
                f"Invalid extension '{suffix}'. Only .md and .canvas files are allowed."
            )
        return resolved

    def _validate_file(self, file_path: str, *, must_exist: bool = False) -> Path:
        resolved = self._safe_resolve(file_path)
        if must_exist and not resolved.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return resolved

    # ── Core subprocess runner ─────────────────────────────────────────

    async def _run(
        self, args: list[str], input_str: Optional[str] = None, timeout: float = 30.0
    ) -> str:
        stdin = asyncio.subprocess.PIPE if input_str is not None else asyncio.subprocess.DEVNULL
        process = await asyncio.create_subprocess_exec(
            *args,
            stdin=stdin,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(
                    input=input_str.encode("utf-8") if input_str else None
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError(f"Command timed out after {timeout}s")

        if process.returncode != 0:
            err = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(err or f"Exit code {process.returncode}")

        return stdout.decode("utf-8", errors="replace")

    # ── Search ─────────────────────────────────────────────────────────

    async def search_vault(self, query: str, path: Optional[str] = None) -> str:
        """Search vault content using the configured CLI tool."""
        target = self.vault_path
        if path:
            target = self._safe_resolve(path, allow_dir=True)

        if self._is_grep:
            if self.exe_name == "findstr":
                args = self.cli_args + ["/S", "/N", query, f"{target}\\*"]
            else:
                args = self.cli_args + ["-n", query, str(target)]
        elif self._is_powershell:
            args = self.cli_args + [
                "-NoProfile", "-Command",
                f"Get-ChildItem -Recurse '{target}' | "
                f"Select-String -Pattern '{query}' | "
                r"ForEach-Object { \"$($_.Filename):$($_.LineNumber):$($_.Line)\" }",
            ]
        else:
            args = self.cli_args + ["search", query, str(target)]
        return await self._run(args)

    # ── Read ───────────────────────────────────────────────────────────

    async def read_file(self, file_path: str) -> str:
        """Read the full content of a vault note."""
        resolved = self._validate_file(file_path, must_exist=True)
        if self._is_powershell:
            args = self.cli_args + [
                "-NoProfile", "-Command",
                f"Get-Content -LiteralPath '{resolved}'",
            ]
        else:
            args = self.cli_args + ["read", str(resolved)]
        return await self._run(args)

    # ── Write ──────────────────────────────────────────────────────────

    async def write_file(self, file_path: str, content: str) -> str:
        """Create a new note or overwrite an existing one."""
        resolved = self._validate_file(file_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        if self._is_powershell:
            args = self.cli_args + [
                "-NoProfile", "-Command",
                f"$input | Set-Content -LiteralPath '{resolved}' -Encoding UTF8",
            ]
        else:
            args = self.cli_args + ["write", str(resolved)]
        return await self._run(args, input_str=content)

    # ── Append ─────────────────────────────────────────────────────────

    async def append_file(self, file_path: str, content: str) -> str:
        """Append text to the end of an existing note."""
        resolved = self._validate_file(file_path, must_exist=True)
        if self._is_powershell:
            args = self.cli_args + [
                "-NoProfile", "-Command",
                f"$input | Add-Content -LiteralPath '{resolved}' -Encoding UTF8",
            ]
        else:
            args = self.cli_args + ["append", str(resolved)]
        return await self._run(args, input_str=content)
