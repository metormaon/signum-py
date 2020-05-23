import binascii
import secrets
import hashlib
import sys


def generate_random_base_64(length_in_bytes: object = 20) -> str:
    """
    Generates a random BASE64 string, based on byutes as requested
    :param length_in_bytes: number of bytes to randomly generate and convert to BASE64
    :return: a random BASE64 string
    """
    return secrets.token_urlsafe(length_in_bytes)


def validate_hashcash_zeros(hashcash: bytes, zero_count: int) -> bool:
    try:
        hashing = hashlib.sha1()
        hashing.update(hashcash)

        hash_result = hashing.hexdigest()

        # convert from hex to binary and keep leading zeros
        binary_string = (bin(int(hash_result, 16))[2:]).zfill(len(hash_result) * 4)

        return binary_string.startswith('0' * zero_count)

    except Exception as e:
        print(e)
        return False

