#!/usr/bin/env python3
"""
basic_auth module
This is the Basic Authentication module for the API
"""
import base64
import binascii
import re
from .auth import Auth
from models.user import User
from typing import Tuple, TypeVar


class BasicAuth(Auth):
    """ Basic authentication class """
    def extract_user_credentials(
            self,
            decoded_base64_authorization_header: str,
            ) -> Tuple[str, str]:
        """ Extracts user credentials from a base64-decoded authorization """
        if type(decoded_base64_authorization_header) == str:
            pattern = r'(?P<user>[^:]+):(?P<password>.+)'
            field_match = re.fullmatch(
                pattern,
                decoded_base64_authorization_header.strip(),
            )
            if field_match is not None:
                user = field_match.group('user')
                passwd = field_match.group('password')
                return user, passwd
        return None, None

    def user_object_from_credentials(
            self,
            user_email: str,
            user_pwd: str) -> TypeVar('User'):
        """ Retrieve user based on the user authentication credentials """
        if type(user_email) == str and type(user_pwd) == str:
            try:
                users = User.search({'email': user_email})
            except Exception:
                return None
            if len(users) <= 0:
                return None
            if users[0].is_valid_password(user_pwd):
                return users[0]
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """ Retrieves the user from a request """
        auth_header = self.authorization_header(request)
        b64_auth_token = self.extract_base64_authorization_header(auth_header)
        auth_token = self.decode_base64_authorization_header(b64_auth_token)
        email, passwd = self.extract_user_credentials(auth_token)
        return self.user_object_from_credentials(email, passwd)

    def extract_base64_authorization_header(
            self,
            authorization_header: str) -> str:
        """ Extracts Base64 part of Authorization header """
        if type(authorization_header) == str:
            pattern = r'Basic (?P<token>.+)'
            field_matchs = re.fullmatch(pattern, authorization_header.strip())
            if field_matchs is not None:
                return field_matchs.group('token')
        return None

    def decode_base64_authorization_header(
            self,
            base64_authorization_header: str,
            ) -> str:
        """ Decodes base64-encoded authorization header """
        if type(base64_authorization_header) == str:
            try:
                resp = base64.b64decode(
                    base64_authorization_header,
                    validate=True,
                )
                return resp.decode('utf-8')
            except (binascii.Error, UnicodeDecodeError):
                return None
