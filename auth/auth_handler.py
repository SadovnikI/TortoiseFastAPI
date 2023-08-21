import time
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from models.user_models import User

# TODO: move to .env file
JWT_SECRET = 'please_please_update_me_pleas'
JWT_ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Auth:
    """
    Authentication manager
    """

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Returns password hashed by bcrypt

        :param password: string that will be hashed by bcrypt.
        """
        return bcrypt.hash(password)

    @classmethod
    def verify_password(cls, password: str, hash_string: str) -> bool:
        """
        Verifies unhashed password by comparing with the hashed password

       :param password: string of unhashed password.
       :param hash_string: string of hashed password.
       """
        return bcrypt.verify(password, hash_string)

    @staticmethod
    def get_token(data: dict, expires_delta: int):
        """
        Generates JWT token based on user data

       :param data: dict of user data.
       :param expires_delta: integer of seconds before JWT expires.
       """
        to_encode = data.copy()
        to_encode.update({
            "exp": datetime.utcnow() + timedelta(seconds=expires_delta),
        })
        return jwt.encode(
            to_encode,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes JWT token and returns decoded data if token is valid

        :param token: JWT access token.
        """
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return decoded_token if decoded_token["exp"] >= time.time() else None
        except:
            return {}

    @classmethod
    async def get_current_user(cls, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
        """
        Helper function that allows to get currently authenticated user inside API endpoint and
        make endpoint JWT protected

        :param token: JWT access token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = cls.decode_token(token)
            username: str = payload.get("email")
            if username is None:
                raise credentials_exception
        except:
            raise credentials_exception
        user = await User.get_or_none(email=username)
        if user is None:
            raise credentials_exception
        return user
