import os
import httpx

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class RecaptchaNotConfiguredError(RuntimeError):
    pass


async def verify_recaptcha(token: str, remote_ip: str | None = None) -> bool:
    if not RECAPTCHA_SECRET_KEY:
        raise RecaptchaNotConfiguredError("reCAPTCHA is not configured")

    if not token:
        return False

    data = {"secret": RECAPTCHA_SECRET_KEY, "response": token}
    if remote_ip:
        data["remoteip"] = remote_ip

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(RECAPTCHA_VERIFY_URL, data=data)
        response.raise_for_status()
        result = response.json()

    return bool(result.get("success"))
