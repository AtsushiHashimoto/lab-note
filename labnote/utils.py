import sys
import os
import json
import re
import ipykernel
import requests
import warnings
import stat

import errno

def is_executed_on_ipython():
    try:
        if "ipykernel" in sys.argv[0]:
            return True
        return False
    except:
        return False

class import_from_backup():
    def __init__(self,backup_dir,link_name):
        self.backup_dir = backup_dir
        self.link_name = link_name
    
    def __enter__(self):
        symlink_force(self.backup_dir,self.link_name)
        return self

    def __exit__(self, ex_type, ex_value, trace):
        os.remove(self.link_name)

def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e

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



def remove_write_permissions(path):
    """Remove write permissions from this path, while keeping all other permissions intact.

    Params:
        path:  The path whose permissions to alter.
    """
    NO_USER_WRITING = ~stat.S_IWUSR
    NO_GROUP_WRITING = ~stat.S_IWGRP
    NO_OTHER_WRITING = ~stat.S_IWOTH
    NO_WRITING = NO_USER_WRITING & NO_GROUP_WRITING & NO_OTHER_WRITING

    current_permissions = stat.S_IMODE(os.lstat(path).st_mode)
    os.chmod(path, current_permissions & NO_WRITING)

def replace_ext(path,ext):
    base,_ = os.path.splitext(path)
    return base + ext
    
def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)


# from https://github.com/jupyter/notebook/issues/1000
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
    try:
        kernel_id = re.search('kernel-(.*).json',
                              ipykernel.connect.get_connection_file()).group(1)
        servers = list_running_servers()
        for ss in servers:
            response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                    params={'token': ss.get('token', '')})
            for nn in json.loads(response.text):
                if nn['kernel']['id'] == kernel_id:
                    relative_path = nn['notebook']['path']
                    return os.path.basename(relative_path)
                    #return os.path.join(ss['notebook_dir'], relative_path)
        warnings.warn('Unexpected Error: no kernel corresponds to this call was found.')
        return None
    except:
        return None
