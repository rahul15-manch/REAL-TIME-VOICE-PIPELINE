"""
Pipeline custom exceptions.
"""

class PipelineError(Exception):
    """Base exception for all pipeline errors."""


class InvalidPipelineError(PipelineError):
    """Raised when a pipeline definition fails validation."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid Pipeline: {message}")


class DuplicateProcessorError(InvalidPipelineError):
    """Raised when trying to add a processor with an ID that already exists."""


class ProcessorNotFoundError(PipelineError):
    """Raised when trying to reference a processor that doesn't exist."""
    
    def __init__(self, processor_id: str) -> None:
        self.processor_id = processor_id
        super().__init__(f"Processor '{processor_id}' not found in pipeline.")


class CircularDependencyError(InvalidPipelineError):
    """Raised when a cycle is detected in the pipeline graph."""


class EmptyPipelineError(InvalidPipelineError):
    """Raised when trying to build an empty pipeline."""
