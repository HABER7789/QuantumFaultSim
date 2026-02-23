from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class CircuitConfig(BaseModel):
    """Configuration for surface code circuit generation."""

    distance: int = Field(ge=3, description="Code distance, must be >= 3 and odd.")
    rounds: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of measurement rounds. Defaults to distance.",
    )
    noise_model: Literal["circuit_level", "phenomenological"] = Field(
        default="circuit_level", description="Type of noise model to apply."
    )
    p: float = Field(ge=0.0, le=1.0, description="Physical error rate probability.")

    @model_validator(mode="after")
    def check_distance_odd(self) -> "CircuitConfig":
        if self.distance % 2 == 0:
            raise ValueError("Surface code distance must be an odd integer.")
        if self.rounds is None:
            self.rounds = self.distance
        return self


class SweepConfig(BaseModel):
    """Configuration for a parallel threshold sweep."""

    distances: List[int] = Field(
        min_length=1, description="List of code distances to sweep."
    )
    noise_values: List[float] = Field(
        min_length=1, description="List of physical error rates to sweep."
    )
    noise_model: Literal["circuit_level", "phenomenological"] = Field(
        default="circuit_level"
    )
    num_workers: int = Field(
        default=4, ge=1, description="Number of CPU worker processes."
    )
    max_shots: int = Field(
        default=500_000, ge=100, description="Maximum shots per parameter point."
    )
    max_errors: int = Field(
        default=500,
        ge=10,
        description="Target logical errors to collect before stopping early.",
    )
    save_resume_filepath: Optional[str] = Field(
        default=None, description="Path to Sinter working file for checkpointing."
    )

    @model_validator(mode="after")
    def check_distances_odd(self) -> "SweepConfig":
        for d in self.distances:
            if d % 2 == 0:
                raise ValueError(
                    f"All distances must be odd, found an even distance: {d}"
                )
        return self
