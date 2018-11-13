from easydict import EasyDict as edict
import yaml
import json
import pickle
import os
import sys
import labnote.utils as utils
from warnings import warn
from datetime import datetime as dt
import shutil
import inspect

from IPython import get_ipython

# 改善点
# 1. from x import func のfuncを検出する術がない ⇢ 今は，できるだけimport moduleとしてもらうことでしか対応できない.
# 2. jupyterやipythonで，script名を取得できない ⇢ constructorで入れてもらう(ipythonのときだけ)

class Note():
    def __init__(self, 
                 log_dir, 
                 script_name=None,
                 safe_mode=True,
                 remove_write_permission=True,
                 log_format='html',
                ):
        self.dir = utils.trim_slash(log_dir)
        self.safe_mode = safe_mode
        
        # Constant Values
        self.ParamFileBaseName = 'params.yml'
        self.MemoFileBaseName = 'memo.txt'
        self.PickleFileBaseName = 'note.pickle'
        self.DateTimeFormat = "%Y%m%d-%H.%M.%S"

        self.params = edict()
        self.imported_files = []
        self.set_timestamp()
        self.log_format = log_format
        
    
        if isinstance(script_name,str):
            self.script_name = script_name
        elif script_name is None:
            temp = inspect.currentframe().f_back.f_code.co_filename
            if temp[0]=='<' and temp[-1]=='>':
                self.script_name = utils.get_notebook_name()
                if self.script_name is None:
                    # if called from ipython, temp should be like "<ipython-input-15-23f3d88a70cc>"
                    # 将来的に，ここをjupyterに対応させたい(改善点2)
                    warn("Please set a correct script name manually!")
                    warn("ex) note.script_name = xxx.ipynb")
                    if self.safe_mode:
                        raise RuntimeError("Failed to get script_name automatically.")
                    
            else:
                self.script_name = temp
        else:
            raise RuntimeError("script_name is not a string.")
        self.reproduction = False
        self.current_dir = os.getcwd()
        self.wrapup_done = False
        if self._check_reproduction(os.getcwd()):
            self._load_me()
            self.reproduction = True
            # change current directory to log_dir.
            self.current_dir = os.getcwd()
            self.dir = self.current_dir
            self.wrapup_done = False

    def __del__(self):
        self.wrapup(self.log_format)
        
    def _check_reproduction(self,current_dir):
        file = os.path.join(current_dir,self.PickleFileBaseName)
        if os.path.exists(file):
            warn("`note.pickle' file found in the current directory. Run in a reproduction mode.")
            return True
        return False
    
    
    @property
    def dirname(self):        
        base_name,_ = os.path.splitext(self.script_name)
        if self.reproduction:
            return self.dir
        else:
            return os.path.join(self.dir,"%s-%s"%(base_name,self.timestamp))
    
    def makedirs(self):
        dirname = self.dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname
    
    
    def set_timestamp(self,ts=None):
        if ts is None:
            self.timestamp = dt.now().strftime(self.DateTimeFormat)
        else:
            self.timestamp = ts

    def get_timestamp(self):
        return self.timestamp
    
    def _safe_file_overwrite(self, path):
        if os.path.isfile(path):
            warn("File is already exist: '%s'"%path)
            if self.safe_mode:
                raise RuntimeError("Stop the program. If you need to overwrite the above file, set safe_mode=False.")
            else:
                warn("The above file will be overwritten. If prevent such an overwrite, set safe_mode=True")

    def set_params(self, params):
        if self.reproduction:
            warn("Caution: change parameters after using them may cause false reproduction results. Please be sure to call Note.set_params before starting experiment.")
            return
        old_keys = list(self.params.keys())
        for k,v in params.items():
            if k in old_keys and self.params[k] is not None:
                warn("%s is going to be overwritten."%k)
                if self.safe_mode:
                    raise RuntimeError("Stop the program. If you need to overwrite the above param, set safe_mode=False.")
                warn("Overwrite %s: %s -> %s"%(k,self.params[k],params[k]))
            self.params[k] = v
            
    def save(self,memo=None):
        if self.reproduction:
            warn("skip save function in a reproduction mode.")
            return
        self._save_param(self.ParamFileBaseName)
        self._save_scripts()
        if memo:
            self._save_memo(memo,self.MemoFileBaseName)
        self._save_me(self.PickleFileBaseName)
        
    def load_module(self,module,timestamp=None):
        # 指定された保存先ディレクトリのモジュールを読み込む．
        # timestampがNoneの場合は，このインスタンスのtimestampを使って検索する．
        raise NotImplementedError("実装待ち．カレントパスが優先されるなら，保存したmain scriptから実行するなら不要か？")
        pass

    def record(self,sub_dir=None):
        return NoteDir(self,sub_dir)
    

    
    def load(self,dirname):
        if self.reproduction:
            warn("skip load function in a reproduction mode.")
            return
        self._load_param(os.join(dirname,self.ParamFileBaseName))        
        
    def _save_scripts(self):
        self._copy_modules()        
        self._copy_main_script()
        
    def _copy_modules(self):
        modules = []
        for k,v in sys.modules.items():
            if not hasattr(v,'__file__'):        
                continue
            #print(k,v.__file__)
            mdir = v.__file__
            if mdir == self.script_name:
                continue            
            cpath = os.path.commonpath([self.current_dir,mdir])
            if cpath =="/": # test on Windows???
                continue
            modules.append(mdir[mdir.find(cpath):])
        if len(modules)==0:
            return
        dirname = self.makedirs()
        #print(dirname)
        cd_len = len(self.current_dir)
        for mdir in modules:
            if len(mdir)<=cd_len+1:
                dist = dirname
            else:
                dist = os.path.join(dirname,mdir[cd_len+1:])
            dist_dir = os.path.dirname(dist)
            if not os.path.exists(dist_dir):
                os.makedirs(dist_dir)
            shutil.copy2(mdir,dist)
            utils.remove_write_permissions(dist)

            
    def _copy_main_script(self):
        dirname = self.makedirs()
        src = os.path.join(self.current_dir,self.script_name)
        if not os.path.exists(src):
            warn("Please set a correct script name manually!")
            warn("ex) note.script_name = xxx.ipynb")
        else:
            dist = os.path.join(dirname,self.script_name)
            shutil.copy2(src,dist)
            utils.remove_write_permissions(dist)
        
        
    def _save_param(self, base_name):
        params = utils.edict2dict(self.params)
        
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        _, ext_name = os.path.splitext(base_name)
        ext_name=ext_name[1:]
        self._safe_file_overwrite(file)        
        with open(file,'w') as f:
            if utils.case_ignore_in(ext_name,['yml','yaml']):                
                yaml.dump(params,f,default_flow_style=False)
            elif utils.case_ignore_in(ext_name,['json']):
                json.dump(params,f)
            elif utils.case_ignore_in(ext_name,['pickle','pkl']):
                pickle.dump(params,f)
            else:
                warn("unknown extension '%s'"%ext_name)
                warn("labnote.Note supports only 'yml/yaml', 'json', and 'pickle/pkl'")
        utils.remove_write_permissions(file)
       
    def _save_memo(self,memo,base_name):
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        self._safe_file_overwrite(file)        
        with open(file,'wb') as f:
            f.write(memo.encode('utf-8'))
        utils.remove_write_permissions(file)
        
    def _load_me(self):
        file = os.path.join(self.current_dir,self.PickleFileBaseName)
        with open(file, 'rb') as f:
            tmp_dict = pickle.load(f)
        self.__dict__.clear()
        self.__dict__.update(tmp_dict) 

    def wrapup(self,to='html'):  
        if self.wrapup_done:
            return
        if not utils.is_executed_on_ipython():
            return
        if to not in ['html','pdf']:
            raise RuntimeError("Unsupported log type: `%s'"%to)
        dirname = self.makedirs()
        basename, _ = os.path.splitext(self.script_name)
        file = os.path.join(dirname,"%s.%s"%(basename,to))
        self._safe_file_overwrite(file)     
        ipython = get_ipython()
        ipython.system("jupyter nbconvert --to %s --output %s %s"%(to,file,self.script_name))
        utils.remove_write_permissions(file)
        self.wrapup_done = True

        

    def _save_me(self,base_name):
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        self._safe_file_overwrite(file)        
        with open(file, 'wb') as f:
            pickle.dump(self.__dict__, f, 2)
        utils.remove_write_permissions(file)
        
    def _load_param(self,file):
        if not os.path.isfile(path):
            warn("File not found: '%s'"%path)
            
        _, ext_name = os.path.splitext(file)
        with open(file,'r+') as f:
            if utils.case_ignore_in(ext_name,['yml','yaml']):
                new = yaml.load(f)
            elif utils.case_ignore_in(ext_name,['json']):
                new = json.load(f)
            elif utils.case_ignore_in(ext_name,['pickle','pkl']):
                new = pickle.load(f)
            else:
                warn("unknown extension '%s'"%ext_name)
                warn("labnote.Note supports only 'yml/yaml', 'json', and 'pickle/pkl'")
                if self.safe_mode:
                    raise RuntimeError('failed to load params')
        self.set_params(new)
    
class NoteDir():
    def __init__(self,note,sub_dir=None):
        self.DateTimeFormat = "%Y%m%d-%H.%M.%S.%f"
        self.note=note
        self.dirname = os.path.join(note.dirname,'results',dt.now().strftime(self.DateTimeFormat))
        if sub_dir:
            self.dirname = os.path.join(self.dirname,sub_dir)
            
        self.opened_dirname = None
        
    def getpath(basename):
        return os.path.join(self.dirname,basename)
    
    def mkdir(basepath):
        dirname = self.getpath(basepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname
            
    def __enter__(self):
        return self.open()
    
    def open(self,dirname=None):
        # create dir
        if dirname is None:
            dirname = self.dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        else:
            warn('%s is already exists. Files in the directory should not be overwritten!!'%dirname)
            if self.note.safe_mode:
                raise RuntimeError('result recording directory was unexpectedly opened twice.')
        self.opened_dirname = dirname
        self.timestamp('Start record')
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.close()
    
    def timestamp(self,comment):
        file = os.path.join(self.dirname,'timestamp')
        mode = 'a'
        if not os.path.exists(file):
            mode = 'w'
        with open(file,mode) as f:
            f.write("%s, %s\n"%(comment,dt.now().strftime(self.DateTimeFormat)))
        
    def close(self):
        # make all files read-only
        exist_file = False
        for file in utils.find_all_files(self.opened_dirname):
            if os.path.isdir(file):
                continue
            if os.path.basename(file)=='timestamp':
                continue
            utils.remove_write_permissions(file)
            exist_file=True
        if not exist_file:
            warn("No file is produced. Remove the directory.")
            os.rmdir(self.opened_dirname)
        else:
            self.timestamp('End record')
        self.opened_dirname = None