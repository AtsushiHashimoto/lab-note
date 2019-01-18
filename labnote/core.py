from easydict import EasyDict as edict
import yaml
import json
import pickle
import os
import sys
import labnote.utils as utils
from labnote.argparse import ArgumentParser as AP
from warnings import warn
from datetime import datetime as dt
import shutil
import inspect
import pip

from subprocess import check_call

from IPython import get_ipython

# 改善点
# 1. from x import func のfuncを検出する術がない ⇢ 今は，できるだけimport moduleとしてもらうことでしか対応できない.
# 2. jupyterやipythonで，script名を取得できない ⇢ constructorで入れてもらう(ipythonのときだけ)

class Note():
    def __init__(self, 
                 log_dir=None,
                 description=None,
                 use_subdir=False,
                 script_name=None,
                 log_format='html',
                 arguments=None,
                ):

        self.description = description
        
        arguments = utils.to_list(arguments)
        self.params = edict()
        for arg in arguments:
            self.update_params(arg)
        # alias of params
        self.args = self.params
        
        if self.params.output is not None:
            log_dir = self.params.output
        
        # Constant Values
        self.ParamFileBaseName = 'params.yml'
        self.MemoFileBaseName = 'memo.txt'
        self.PickleFileBaseName = 'note.pickle'
        self.DateTimeFormat = "%Y%m%d-%H.%M.%S"

        self.imported_files = []
        self.set_timestamp()
        self.log_format = log_format

        if log_dir is None:
            log_dir = 'output'
            warn('output directory has not been set. We use "./output" for distination.')
            
        self.use_subdir = use_subdir
        self.dir = utils.trim_slash(log_dir)        
    
        if utils.is_executed_on_ipython():
            self.script_name = utils.get_notebook_name()
            if self.script_name is None:
                # if called from ipython, temp should be like "<ipython-input-15-23f3d88a70cc>"
                # 将来的に，ここをjupyterに対応させたい(改善点2)
                if isinstance(script_name,str):
                    self.script_name = script_name
                else:                    
                    warn("Please set your script file name to 'script_name'.")
                    warn("ex) note.script_name = xxx.ipynb")
                    warn("NOTE: This warning may happen if you are using jupyter in a docker, and access via port-forwarding. Using jupyter with password authentification can be another possibility.")
                    self.script_name = 'main'
        else:
            self.script_name = inspect.currentframe().f_back.f_code.co_filename
            
        self.reproduction = False
        self.current_dir = os.getcwd()
        self.wrapup_done = False
        if self._check_reproduction(os.getcwd()):
            # requirementsのdiffを表示させたい(改善点3)

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
    
    def update_params(self,arg,level=0):
        if isinstance(arg,dict):
            pass
        elif isinstance(arg,str):
            if level==0:
                parser = self.create_argparse_from_yaml(arg)            
                arg = parser.parse_args()
            else:
                with open(arg,'r') as f:
                    arg = yaml.load(f)
        for k,v in arg.items():
            self.params[k]=v
            
        # update by config file after update arg.
        # this is to maintain priority of the settings (use config file when values for a key is duplicated).
        if 'config' in arg.keys():
            configs = utils.to_list(arg['config'])
            [self.update_params(conf,level=level+1) for conf in configs]
            
    def create_argparse_from_yaml(self,path):
        with open(path,'r') as f:
            actions = yaml.load(f)
        parser = AP()
        
        for var_name,act in actions.items():
            name = ['--%s'%var_name]
            if 'name' in act.keys():
                name += utils.to_list(act['name'])
                act.pop('name')
            _type = None
            if '_type' in act.keys():
                _type = utils.get_type(act['_type'])
                act.pop('_type')
            if 'type' in act.keys():
                _type = utils.get_type(act['type'])
                act.pop('type')
            parser.add_argument(*name,type=_type,**act) 
        return parser
    @property
    def dirname(self):
        if not self.use_subdir:
            return self.dir
        # generate subdir name.
        base_name,_ = os.path.splitext(self.script_name)
        if self.reproduction:
            return self.dir
        return os.path.join(self.dir,base_name,self.timestamp)
        
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
            warn("The above file will be overwritten.")
            
    def set_params(self, params):
        if self.reproduction:
            warn("Caution: change parameters after using them may cause false reproduction results. Please be sure to call Note.set_params before starting experiment.")
            return
        old_keys = list(self.params.keys())
        for k,v in params.items():
            if k in old_keys and self.params[k] is not None:
                warn("%s is going to be overwritten."%k)
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

    def record(self,sub_dir=None,timestamped_dir=None):
        if timestamped_dir is None:
            timestamped_dir = self.use_subdir
        return NoteDir(self,sub_dir,timestamped_dir=timestamped_dir)
    

    
    def load(self,dirname):
        if self.reproduction:
            warn("skip load function in a reproduction mode.")
            return
        self._load_param(os.path.join(dirname,self.ParamFileBaseName))        
        
    def _save_scripts(self):
        self._copy_main_script()
        self._copy_modules()        
        
        
    def _copy_modules(self):
        dirname = self.makedirs()
        modules = []
        
        for k,v in sys.modules.items():
            if not hasattr(v,'__file__'):        
                continue
            #print(k,v.__file__)
            mdir = v.__file__
            if mdir == self.script_name:
                continue            
            cpath = os.path.commonpath([self.current_dir,mdir])
            if len(cpath) != len(self.current_dir):
                continue
            modules.append(mdir[mdir.find(cpath):])

        # generate requirements.txt
        try:
            check_call(['pipreqs','--encoding','utf-8','--save',os.path.join(dirname,'requirements.txt'),dirname])
        except:
            warn("Failed to pipreqs, which generates 'requirements.txt'. Typically, this is caused by a syntax error in your code.")
        
        # copy all original modules
        if len(modules)==0:
            return
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
            
        basename,_ = os.path.splitext(self.script_name)
           

    def _copy_main_script(self):
        dirname = self.makedirs()
        src = os.path.join(self.current_dir,self.script_name)
        if not os.path.exists(src):
            warn("Please set a correct script name manually!")
            warn("ex) note.script_name = xxx.ipynb")
        else:
            dist = os.path.join(dirname,self.script_name)
            shutil.copy2(src,dist)
        _,ext = os.path.splitext(self.script_name)

        if not utils.is_executed_on_ipython():
            return
        
        
        script_head,_ = os.path.splitext(self.script_name)
        script_head = os.path.join(dirname,script_head)        
        ipython = get_ipython()
        ipython.system("jupyter nbconvert --to script --output %s %s"%(script_head,self.script_name))
        
        
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
       
    def _save_memo(self,memo,base_name):
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        self._safe_file_overwrite(file)        
        with open(file,'wb') as f:
            if self.description is not None:
                f.write(self.description.encode('utf-8'))
                f.write("\n".encode('utf-8'))
                
            f.write(memo.encode('utf-8'))
            f.write("\n".encode('utf-8'))
        
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
        self.wrapup_done = True

        

    def _save_me(self,base_name):
        dirname = self.makedirs()
        file = os.path.join(dirname,base_name)
        self._safe_file_overwrite(file)        
        with open(file, 'wb') as f:
            pickle.dump(self.__dict__, f, 2)
        
    def _load_param(self,file):
        if not os.path.isfile(file):
            warn("File not found: '%s'"%file)
            
        _, ext_name = os.path.splitext(file)
        ext_name=ext_name[1:]
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
        self.set_params(new)
    
class NoteDir():
    def __init__(self,note,sub_dir=None,timestamped_dir=False):
        self.DateTimeFormat = "%Y%m%d-%H.%M.%S.%f"
        self.note=note
        if timestamped_dir:
            self.dirname = os.path.join(note.dirname,'results',dt.now().strftime(self.DateTimeFormat))
        else:
            self.dirname = os.path.join(note.dirname,'results')           
        if sub_dir:
            self.dirname = os.path.join(self.dirname,sub_dir)
            
        self.opened_dirname = None
        
    def getpath(self,basename):
        return os.path.join(self.dirname,basename)
    
    def mkdir(self,basepath):
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
            warn('%s is already exists. Files in the directory will be overwritten.'%dirname)
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
            time=dt.now().strftime(self.DateTimeFormat)
            print("%s, %s\n"%(comment,time))
            f.write("%s, %s\n"%(comment,time))
        
    def close(self):
        if self.opened_dirname is None:
            warn('You must open the recording directory before close it.')
            return 
        # make all files read-only
        exist_file = False
        for file in utils.find_all_files(self.opened_dirname):
            if os.path.isdir(file):
                continue
            if os.path.basename(file)=='timestamp':
                continue
            exist_file=True
        self.timestamp('End record')
        self.opened_dirname = None
