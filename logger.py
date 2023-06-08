import logging
import logging.handlers
import os

def loggerInit():
    logging.basicConfig(level=logging.INFO)

    loggerDevelop = logging.getLogger('develop')
    loggerDevelop.setLevel(logging.INFO)

    loggerAudit = logging.getLogger('audit')
    loggerAudit.setLevel(logging.INFO)
    log_path = os.path.join(os.curdir, 'logs')
    if os.path.exists(log_path) == False:
        os.makedirs(log_path)
    if os.path.isfile(os.path.join(log_path, 'log.txt')) == False:
        open(os.path.join(log_path, 'log.txt'), 'w').close()
    handler = logging.FileHandler(filename=os.path.join(log_path, 'log.txt'), mode="a")
    loggerAudit.addHandler(handler)
    
