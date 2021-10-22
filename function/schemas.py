from dataclasses import dataclass
from typing import Optional


@dataclass
class MailMessage:
    recipient: str
    sender: str
    subject: str
    html_content: Optional[str]
    text_content: Optional[str]
