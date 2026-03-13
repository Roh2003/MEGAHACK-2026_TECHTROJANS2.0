from urllib.parse import quote


def generate_whatsapp_share_link(
    job_url: str,
    message: str = "Exciting job opportunity! Apply now.",
) -> str:
    """
    Generate a WhatsApp share link for a job posting.

    The `text` query parameter populates the WhatsApp message body.
    Works for both mobile deep-links and the WhatsApp Web client.
    """
    text = f"{message} {job_url}"
    encoded_text = quote(text, safe="")
    return f"https://wa.me/?text={encoded_text}"
