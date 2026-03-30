from __future__ import annotations

import asyncio
import hashlib
from typing import Optional


def _encrypt(seed: str, password: str) -> str:
    return hashlib.sha256(f"{seed}{password}".encode()).hexdigest()


async def adcp_exchange(
    host: str,
    port: int,
    password: Optional[str],
    command: str,
    timeout: float = 5.0,
) -> Optional[str]:
    """Minimal ADCP line-based exchange over TCP (Python 3.13-safe).

    Flow:
    - Connect TCP
    - Read banner line
    - If banner != NOKEY*, send sha256(seed+password) and expect OK
    - Send command
    - Read single-line reply
    """
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        try:
            banner = (await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout)).decode().strip()

            if not banner.startswith("NOKEY"):
                if not password:
                    return None
                writer.write((_encrypt(banner, password) + "\r\n").encode())
                await writer.drain()
                auth_resp = (await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout)).decode().strip()
                if auth_resp != "OK":
                    return None

            writer.write((command + "\r\n").encode())
            await writer.drain()

            reply = (await asyncio.wait_for(reader.readuntil(b"\r\n"), timeout=timeout)).decode().strip()
            return reply
        finally:
            writer.close()
            await writer.wait_closed()
    except (OSError, asyncio.TimeoutError, asyncio.IncompleteReadError):
        return None
