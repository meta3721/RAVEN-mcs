"""Reject cross-method reuse of Design-dependent artifacts before deserialization."""
from typing import Any, Mapping
from pathlib import Path
import json
from raven_mcs.sag.r1l_design import DesignConfiguration


def configured_cache_identity(configuration: DesignConfiguration, **dependencies: Any) -> dict[str, Any]:
    return {
        "method_version": configuration.method_version,
        "design_configuration": configuration.to_dict(),
        "coverage_role": "diagnostic_only",
        "dependencies": dependencies,
    }


def validate_configured_cache(metadata: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    """Raw data/splits do not use this guard; weights/models/predictions do."""
    if not expected.get("dependencies"):
        raise ValueError("CACHE_IDENTITY_ERROR: exact computational dependencies required")
    if dict(metadata) != dict(expected):
        raise ValueError("CACHE_IDENTITY_ERROR: regenerate Design-dependent artifact; legacy or unversioned cache cannot be reused")


def load_configured_artifact(path: Path, expected: Mapping[str, Any]) -> Any:
    """Require the exact identity sidecar before reading weights or predictions."""
    path = Path(path)
    sidecar = path.with_suffix(path.suffix + ".identity.json")
    if not sidecar.is_file():
        raise ValueError("CACHE_IDENTITY_ERROR: missing configured artifact provenance; regenerate")
    validate_configured_cache(json.loads(sidecar.read_text(encoding="utf-8")), expected)
    import torch
    return torch.load(path, map_location="cpu", weights_only=True)
