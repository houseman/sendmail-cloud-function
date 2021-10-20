from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MailMessage:
    recipient: str
    sender: str
    subject: str
    html_content: Optional[str]
    text_content: Optional[str]


@dataclass
class ControllerResponse:
    response_code: int
    message: str


@dataclass
class ApiResponse:
    response_code: int
    message: str
