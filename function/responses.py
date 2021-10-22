from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ControllerResponse:
    response_code: int
    message: str


@dataclass
class ApiResponse:
    response_code: int
    message: str
