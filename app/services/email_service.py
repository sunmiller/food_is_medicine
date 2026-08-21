import os
import httpx

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER", f"Eat for Healing <postmaster@{MAILGUN_DOMAIN}>")
CONTACT_RECIPIENT_EMAIL = os.getenv("CONTACT_RECIPIENT_EMAIL")


class EmailNotConfiguredError(RuntimeError):
    pass


async def send_contact_email(name: str, email: str, message: str) -> None:
    if not (MAILGUN_API_KEY and MAILGUN_DOMAIN and CONTACT_RECIPIENT_EMAIL):
        raise EmailNotConfiguredError("Mailgun is not configured")

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_SENDER,
                "to": CONTACT_RECIPIENT_EMAIL,
                "h:Reply-To": email,
                "subject": f"New contact form message from {name}",
                "text": f"From: {name} <{email}>\n\n{message}",
            },
        )
        response.raise_for_status()
