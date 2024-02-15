#!/usr/bin/env python3
"""
Session authentication with expiration and storage module for the API
"""
from .session_exp_auth import SessionExpAuth
from datetime import datetime, timedelta
from flask import request
from models.user_session import UserSession


class SessionDBAuth(SessionExpAuth):
    """ Session authentication class with expiration and db storage """

    def create_session(self, user_id=None) -> str:
        """ Creates and stores session id for the user """
        session_id = super().create_session(user_id)
        if type(session_id) == str:
            kwargs = {
                'user_id': user_id,
                'session_id': session_id,
            }
            user_session = UserSession(**kwargs)
            user_session.save()
            return session_id

    def user_id_for_session_id(self, session_id=None):
        """ Returns the user id of the user associated with
        a given session id """
        try:
            user_sessions = UserSession.search({'session_id': session_id})
        except Exception:
            return None
        if len(user_sessions) <= 0:
            return None
        current_time = datetime.now()
        time_span = timedelta(seconds=self.session_duration)
        exp_time = user_sessions[0].created_at + time_span
        if exp_time < current_time:
            return None
        return user_sessions[0].user_id

    def destroy_session(self, request=None) -> bool:
        """ Destroys authenticated session """
        session_id = self.session_cookie(request)
        try:
            user_sessions = UserSession.search({'session_id': session_id})
        except Exception:
            return False
        if len(user_sessions) <= 0:
            return False
        user_sessions[0].remove()
        return True
