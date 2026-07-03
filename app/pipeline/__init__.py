"""
Pipeline Builder Package — Assembles immutable execution graphs.
"""

from .builder import PipelineBuilder
from .exceptions import (
    CircularDependencyError,
    DuplicateProcessorError,
    EmptyPipelineError,
    InvalidPipelineError,
    PipelineError,
    ProcessorNotFoundError,
)
from .factory import PipelineFactory
from .graph import PipelineGraph
from .models import Pipeline
from .processors import ProcessorNode, ProcessorRole
from .serializer import PipelineSerializer
from .validators import validate_pipeline

__all__ = [
    "PipelineBuilder",
    "PipelineFactory",
    "PipelineGraph",
    "Pipeline",
    "ProcessorNode",
    "ProcessorRole",
    "PipelineSerializer",
    "validate_pipeline",
    "PipelineError",
    "InvalidPipelineError",
    "DuplicateProcessorError",
    "ProcessorNotFoundError",
    "CircularDependencyError",
    "EmptyPipelineError",
]
