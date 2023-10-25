'''
Do something useful by schedule
'''
from datetime import datetime 

NOW = datetime.now()


if NOW.minute == 0: # run every hour
    pass # clear cache or send messages
