"""Abstract base interface for Renderer Adapters."""

from abc import ABC, abstractmethod
from .schemas import RenderPackage

class RendererAdapterInterface(ABC):
    @abstractmethod
    def execute_render(self, package: RenderPackage) -> bool:
        """
        Accepts a finalized RenderPackage and hands it off to the runtime engine (e.g. Godot).
        Returns True if handed off successfully.
        """
        pass
