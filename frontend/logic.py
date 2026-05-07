import requests

API_URL = "http://127.0.0.1:8000"


def get_match_tt(fuse_value):
    """Просто ищет строку в базе и возвращает её"""
    if not fuse_value:
        return None
    try:
        response = requests.get(f"{API_URL}/refs/TT_RATING")
        if response.status_code == 200:
            tt_options = response.json()
            # Ищем совпадение (напр. "400" -> "400/5")
            return next(
                (opt for opt in tt_options if opt.startswith(
                    str(fuse_value))), None)
    except BaseException:
        return None
    return None
