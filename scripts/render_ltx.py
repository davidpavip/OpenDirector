from __future__ import annotations

import asyncio
from pathlib import Path

from opendirector.animation import (
    LTXAnimationProvider,
    LTXOptions,
)
from opendirector.applications import AnimateApplication


async def main() -> None:
    provider = LTXAnimationProvider(
        options=LTXOptions(
            model="ltx-2-3-fast",
            resolution="1920x1080",
            generate_audio=True,
        )
    )

    clip = await AnimateApplication(
        provider=provider,
    ).run(
        production_dir=Path("productions/little_robot"),
        scene_id="scene-001",
        shot_id="shot-001",
        duration_seconds=6.0,
    )

    print()
    print("=" * 60)
    print("✓ LTX render completed")
    print("=" * 60)
    print(f"Clip:     {clip.artifact.location}")
    print(f"Provider: {clip.provider_id}")
    print(f"Duration: {clip.duration_seconds:g} seconds")
    print(f"Audio:    {clip.has_audio}")


if __name__ == "__main__":
    asyncio.run(main())