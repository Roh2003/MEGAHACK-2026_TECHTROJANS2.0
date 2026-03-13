from urllib.parse import quote


def generate_linkedin_share_link(job_url: str) -> str:
    """
    Generate a LinkedIn share link for a job posting.

    LinkedIn's share endpoint accepts a `url` query parameter which renders
    a rich preview when the user shares it on their feed.
    """
    encoded_url = quote(job_url, safe="")
    return f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
