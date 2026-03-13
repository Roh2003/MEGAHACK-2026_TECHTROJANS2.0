import os
from dotenv import load_dotenv

from adapters.linkedin_adapter import generate_linkedin_share_link
from adapters.twitter_adapter import generate_twitter_share_link
from adapters.whatsapp_adapter import generate_whatsapp_share_link

load_dotenv()

BASE_JOB_URL: str = os.getenv("BASE_JOB_URL", "http://localhost:8002")
_SHARE_MESSAGE = "Exciting job opportunity! Apply now."


async def distribute_job(job_id: str) -> dict:
    """
    Build social media share links for a given job ID.

    The job URL is constructed from BASE_JOB_URL and job_id.
    No external HTTP calls are made; links are generated locally.
    """
    job_url = f"{BASE_JOB_URL}/jobs/{job_id}"

    return {
        "job_id": job_id,
        "job_url": job_url,
        "share_links": {
            "linkedin": generate_linkedin_share_link(job_url),
            "twitter": generate_twitter_share_link(job_url, _SHARE_MESSAGE),
            "whatsapp": generate_whatsapp_share_link(job_url, _SHARE_MESSAGE),
        },
        "message": "Job distribution links generated successfully",
    }
