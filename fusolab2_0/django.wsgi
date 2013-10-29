import os
import sys
import site
prev_sys_path = list(sys.path)

sys.path.append('/var/www/fusolab/')

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path] 
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

os.environ['DJANGO_SETTINGS_MODULE'] = 'fusolab2_0.settings'
#os.environ['CELERY_LOADER'] = 'django' 

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
