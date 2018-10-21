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

# 改善点
# 1. from x import func のfuncを検出する術がない ⇢ 今は，できるだけimport moduleとしてもらうことでしか対応できない.
# 2. jupyterやipythonで，script名を取得できない ⇢ constructorで入れてもらう(ipythonのときだけ)

class Note():
    '''
    '''
    def __init__(self, 
                 log_dir, 
                 script_name=None,
                 safe_mode=True,
                ):
        self.dir = utils.trim_slash(log_dir)
        self.safe_mode = safe_mode
        
        # Constant Values
        self.ParamFileBaseName = 'params.yml'
        self.DateTimeFormat = "%Y%m%d-%H.%M.%S"

        self.params = edict()
        self.imported_files = []
        self.set_timestamp()
    
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
                    if safe_mode:
                        raise RuntimeError("Failed to get script_name automatically.")
                    
            else:
                self.script_name = temp
        else:
            raise RuntimeError("script_name is not a string.")
        self.current_dir = os.getcwd()
    
    @property
    def dirname(self):
        base_name,_ = os.path.splitext(self.script_name)
        return os.path.join(self.dir,"%s-%s"%(base_name,self.timestamp))
    
    def makedirs(self):
        dirname = self.dirname
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname
    
    def local_modules(self):
        return ImportManager(self)
    
    def set_timestamp(self,ts=None):
        if ts is None:
            self.timestamp = dt.now().strftime(self.DateTimeFormat)
        else:
            self.timestamp = ts

    def get_timestamp(self):
        return self.timestamp
    
    def safe_file_overwrite(self, path):
        if os.path.isfile(path):
            warn("File is already exist: '%s'"%path)
            if safe_mode:
                raise RuntimeError("Stop the program. If you need to overwrite the above file, set safe_mode=False.")
            else:
                warn("The above file will be overwritten. If prevent such an overwrite, set safe_mode=True")

    def set_params(self, params):
        old_keys = list(self.params.keys())
        for k,v in params.items():
            if k in old_keys and self.params[k] is not None:
                warn("%s is going to be overwritten."%k)
                if self.safe_mode:
                    raise RuntimeError("Stop the program. If you need to overwrite the above param, set safe_mode=False.")
                warn("Overwrite %s: %s -> %s"%(k,self.params[k],params[k]))
            self.params[k] = v
            
    def save(self):
        self._save_param(self.ParamFileBaseName)
        self._save_scripts()
        
    def load_module(self,module,timestamp=None):
        # 指定された保存先ディレクトリのモジュールを読み込む．
        # timestampがNoneの場合は，このインスタンスのtimestampを使って検索する．
        raise NotImplementedError("実装待ち．カレントパスが優先されるなら，保存したmain scriptから実行するなら不要か？")
        pass

    def save_result(self,sub_dir='results'):
        return SaveResult(self,sub_dir)
    
    def wrapup(self,exit=False):
        # 自分自身の実行結果をhtmlとして保存
        
        if exit:
            sys.exit()
    
    def load(self,dirname):
        self.load_param(os.join(dirname,self.ParamFileBaseName))        
        
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
            cpath = os.path.commonpath([self.current_dir,mdir])
            if cpath =="/":
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
            
    def _copy_main_script(self):
        dirname = self.makedirs()
        src = os.path.join(self.current_dir,self.script_name)
        if not os.path.exists(src):
            warn("Please set a correct script name manually!")
            warn("ex) note.script_name = xxx.ipynb")
        else:
            dist = os.path.join(dirname,self.script_name)
            shutil.copy2(src,dist)
        
        
    def _save_param(self, base_name):
        params = utils.edict2dict(self.params)
        
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        _, ext_name = os.path.splitext(base_name)
        ext_name=ext_name[1:]
        self.safe_file_overwrite(file)        
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
                  
    def load_param(self,file):
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
    
class SaveResult():
    def __init__(self,note,sub_dir):
        self.note=note
        self.sub_dir = sub_dir
        
    def __enter__(self):
        dst_dir = os.path.join(note.dirname,sub_dir)
        if os.path.exists(dirname):
            
        else:
            os.makedirs(dirname)
        return dst_dir

    
