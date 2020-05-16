import secrets


def generate_random_base_64(length_in_bytes: object = 20) -> str:
    """
    Generates a random BASE64 string, based on byutes as requested
    :param length_in_bytes: number of bytes to randomly generate and convert to BASE64
    :return: a random BASE64 string
    """
    return secrets.token_urlsafe(length_in_bytes)

