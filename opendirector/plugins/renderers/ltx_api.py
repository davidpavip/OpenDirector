from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

import requests

from ...core.models import Shot
from ...core.project import Project
from ...core.renderer import Renderer


class LTXAPIRenderer(Renderer):
    """LTX official API renderer using Base64 data URI input.

    This avoids temporary cloud-storage URI issues and works well for
    reasonably sized storyboard PNGs.
    """

    endpoint = "https://api.ltx.video/v1/image-to-video"

    def __init__(self, api_key: str | None = None, model: str = "ltx-2-3-fast", resolution: str = "1920x1080"):
        self.api_key = api_key or os.environ.get("LTX_API_KEY")
        if not self.api_key:
            raise RuntimeError("LTX_API_KEY is not set")
        self.model = model
        self.resolution = resolution

    @staticmethod
    def _image_to_data_uri(path: Path) -> str:
        mime = mimetypes.guess_type(path)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:{mime};base64,{encoded}"

    def render_shot(self, project: Project, shot: Shot, overwrite: bool = False) -> Path:
        image_path = project.path(shot.image_file)
        output_path = project.path(shot.video_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists() and not overwrite:
            print(f"Skipping existing: {output_path}")
            return output_path

        if not image_path.exists():
            raise FileNotFoundError(f"Missing image for {shot.id}: {image_path}")

        payload = {
            "image_uri": self._image_to_data_uri(image_path),
            "prompt": shot.video_prompt,
            "model": self.model,
            "duration": int(shot.duration),
            "resolution": self.resolution,
            "generate_audio": False,
        }

        print(f"Rendering {shot.id} -> {output_path.name}")
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=900,
        )

        if response.status_code != 200:
            print("LTX error:", response.text[:2000])
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return output_path
