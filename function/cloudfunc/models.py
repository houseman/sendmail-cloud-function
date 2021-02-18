from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MailMessage:
    recipient: str
    sender: str
    subject: str
    html_content: Optional[str]
    text_content: Optional[str]


@dataclass
class TransactionRecord:
    try_count: int = 0
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ControllerResponse:
    response_code: int
    message: str


@dataclass
class ApiResponse:
    response_code: int
    message: str
