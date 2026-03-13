from urllib.parse import quote


def generate_twitter_share_link(
    job_url: str,
    message: str = "Exciting job opportunity! Apply now.",
) -> str:
    """
    Generate a Twitter/X intent share link for a job posting.

    The `text` parameter pre-fills the tweet body with the message and URL.
    """
    text = f"{message} {job_url}"
    encoded_text = quote(text, safe="")
    return f"https://twitter.com/intent/tweet?text={encoded_text}"
