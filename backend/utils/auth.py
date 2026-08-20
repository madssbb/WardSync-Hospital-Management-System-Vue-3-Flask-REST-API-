from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User, Role

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({'msg': 'Unauthorized or suspended account'}), 403
            
            if user.role.name not in roles:
                return jsonify({'msg': 'Forbidden: Insufficient privileges'}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
