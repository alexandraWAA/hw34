import re
from django.core.exceptions import ValidationError


def validate_youtube_url(value):
    if not value:
        return
    youtube_patterns = [
        r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]+",
        r"^https?://(www\.)?youtu\.be/[\w-]+",
        r"^https?://(www\.)?youtube\.com/embed/[\w-]+",
        r"^https?://(www\.)?youtube\.com/shorts/[\w-]+",
    ]
    for pattern in youtube_patterns:
        if re.match(pattern, value):
            return
    raise ValidationError("Разрешены только ссылки на YouTube")
