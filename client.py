# client.py
import asyncio
import httpx
from dataclasses import dataclass
from typing import Optional, Any
import subprocess
import time


@dataclass
class StepResult:
    observation: Any
    reward: float
    done: bool


class ObsWrapper:
    """Wraps raw dict so inference.py can use dot notation: obs.ticket_id etc."""
    def __init__(self, data: dict):
        self._data = data
    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"No field '{name}' in observation")


class OmniSupportEnvClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)
        self._container_name: Optional[str] = None

    @classmethod
    async def from_docker_image(cls, image_name: str, port: int = 7860) -> "OmniSupportEnvClient":
        """Start a Docker container from image and return a connected client."""
        container_name = "omni-inference-run"

        # Stop existing container if any
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm",   container_name], capture_output=True)

        # Start fresh
        subprocess.run([
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{port}:7860",
            image_name
        ], check=True)

        # Wait for it to be healthy
        base_url = f"http://localhost:{port}"
        async with httpx.AsyncClient(timeout=5.0) as probe:
            for _ in range(20):
                await asyncio.sleep(2)
                try:
                    r = await probe.get(f"{base_url}/health")
                    if r.status_code == 200:
                        break
                except Exception:
                    pass

        instance = cls(base_url)
        instance._container_name = container_name
        return instance

    async def reset(self, task_id: Optional[str] = None, **kwargs) -> StepResult:
        payload = {}
        if task_id:
            payload["task_id"] = task_id
        r = await self._client.post(f"{self._base_url}/reset", json=payload)
        r.raise_for_status()
        data = r.json()
        return StepResult(
            observation=ObsWrapper(data["observation"]),
            reward=data.get("reward") or 0.0,
            done=data.get("done", False),
        )

    async def step(self, action) -> StepResult:
        payload = {
            "action": {
                "action_type": action.action_type.value,
                "action_value": action.action_value,
            }
        }
        r = await self._client.post(f"{self._base_url}/step", json=payload)
        r.raise_for_status()
        data = r.json()
        return StepResult(
            observation=ObsWrapper(data["observation"]),
            reward=data.get("reward") or 0.0,
            done=data.get("done", False),
        )

    async def close(self):
        await self._client.aclose()
        if self._container_name:
            subprocess.run(["docker", "stop", self._container_name], capture_output=True)
            subprocess.run(["docker", "rm",   self._container_name], capture_output=True)