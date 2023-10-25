'''
Do something useful by schedule
'''
from datetime import datetime 

NOW = datetime.now()


if NOW.minute == 0: # run every hour - clear expired sessions
    from gae.sessions import delete_expired_sessions
    delete_expired_sessions()
