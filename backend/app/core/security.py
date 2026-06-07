"""
core/security.py
비밀번호 해싱/검증 유틸리티 (bcrypt 사용)

회원가입 시 hash_password()로 평문 비밀번호를 해시하여 저장하고,
로그인 시 verify_password()로 입력값과 저장된 해시를 비교한다.
평문 비밀번호는 절대 DB에 저장하지 않는다.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """평문 비밀번호를 bcrypt 해시 문자열로 변환."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호가 저장된 해시와 일치하는지 검증."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
