from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from shared.email import send_ai_application_result

load_dotenv()


async def main() -> None:
    to_email = os.getenv("TEST_EMAIL_TO") or os.getenv("SMTP_USER")
    if not to_email:
        raise RuntimeError("Set TEST_EMAIL_TO or SMTP_USER in .env before running test.")

    await send_ai_application_result(
        to=to_email,
        candidate_name="Ragini",
        job_title="Machine Learning Engineer",
        status="accepted",
        matching_skills=["Python", "TensorFlow", "Computer Vision"],
        weaknesses=[],
    )

    print(f"Email test completed. Check inbox for: {to_email}")


if __name__ == "__main__":
    asyncio.run(main())
