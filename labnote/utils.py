import sys
def is_executed_on_ipython():
    if "ipykernel_launcher.py" in sys.argv[0]:
        return True
    return False


def case_ignore_in(test, L):
    test = test.lower()
    for l in L:
        if l.lower()==test:
            return True
    return False


def trim_slash(s):
    if len(s)<1:
        return s
    if s[-1] == '/':
        return s[:-1]
    return s

def edict2dict(edict):
    return {k:v for k,v in edict.items()}


# from https://github.com/jupyter/notebook/issues/1000
import json
import os.path
import re
import ipykernel
import requests
import warnings

#try:  # Python 3
#    from urllib.parse import urljoin
#except ImportError:  # Python 2
#    from urlparse import urljoin

# Alternative that works for both Python 2 and 3:
from requests.compat import urljoin

try:  # Python 3 (see Edit2 below for why this may not work in Python 2)
    from notebook.notebookapp import list_running_servers
except ImportError:  # Python 2
    import warnings
    from IPython.utils.shimmodule import ShimWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ShimWarning)
        from IPython.html.notebookapp import list_running_servers


def get_notebook_name():
    """
    Return the full path of the jupyter notebook.
    """
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    servers = list_running_servers()
    for ss in servers:
        response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                params={'token': ss.get('token', '')})
        try:
            for nn in json.loads(response.text):
                if nn['kernel']['id'] == kernel_id:
                    relative_path = nn['notebook']['path']
                    return os.path.join(ss['notebook_dir'], relative_path)
        except:
            warnings.warn("Failed to get script name automatically.")
            warnings.warn("This warning may happen if you are using jupyter in a docker, and access via port-forwarding. Using jupyter with password authentification can be another possibility.")
            pass
        
<<<<<<< HEAD
        
=======
        
>>>>>>> e441e080b54f8e02641198a4d18bdf9b85ce29f1
