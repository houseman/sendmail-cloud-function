from dataclasses import dataclass


@dataclass
class MailMessage:
    recipient: str
    sender: str
    subject: str
    html_content: str | None
    text_content: str | None
