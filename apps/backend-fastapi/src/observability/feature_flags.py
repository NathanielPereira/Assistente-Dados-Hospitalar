from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeatureFlags:
    read_only_mode: bool = False
    rag_enabled: bool = True


flags = FeatureFlags()
