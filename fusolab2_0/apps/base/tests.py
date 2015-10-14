from django.contrib.auth.models import User

def in_turnisti(user):
    if user:
        return user.groups.filter(name='turnisti').count() > 0
    return False
