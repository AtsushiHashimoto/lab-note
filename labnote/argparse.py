from warnings import warn
from easydict import EasyDict as edict
if not is_executed_on_ipython():
    from argparse import ArgumentParser as AP
    
class ArgumentParser(edict):
    '''
    ipythonとpytho環境の両方で動くプログラムのパラメタ管理システム．    
    優先順位: arg_parserのdefault値 < config_fileの値  < parse_argsのkwargsによる指定値 < コマンドラインの設定値
    '''
    def __init__(self,*args,**kwargs):    
        self.ap = AP(args,kwargs)
        self.required = set()
        

        
    def add_argument(self,*args,**kwargs):
        store_action = self.ap.add_argument(*args,**kwargs)
        self[store_action.dest]=store_action.default
        if len(store_action.option_strings)==0:
            # 必須項目
            self.required.add(store_action.dest)            
        return store_action  
                
    def parse_args(self,**kwargs):
        # kwargsで直接指定されていればそれを優先.        
        params = edict(kwargs)
        for k,v in params.items():            
            if k not in self.keys():
                warn("Unknown key value '%s' in %s is ignored."%(key,config_file))
                continue
            self[k] = v

        if is_executed_on_ipython():
            # 引数をtempに退避
            temp = sys.argv
            sys.argv = sys.argv[:1]
            # 必須項目がkwargsに存在するか確認
            for dest in self.required:
                try:
                    if dest not in kwargs.keys():
                        raise RuntimeError("A required parameter '%s' was not given to parse_args as an option.\nex) parse_args(%s)"%(dest,", ".join(["%s=..."%d for d in self.required])))                                           
                    # オリジナルのarg_parseがエラーを起こすので，引数に必須な変数を指定
                    sys.argv.append(kwargs[dest])        


        params = self.ap.parse_args()

        if is_executed_on_ipython():
            # 引数を戻しておく
            sys.argv=temp   
        
            

        # コマンドライン引数はdefault値と異なった場合に採用
        # それ以外はload_configの値を優先.        
        for k,v in params.__dict__.items():
            if k not in self.keys():
                warn("Unknown key value '%s' in %s is ignored."%(key,config_file))
                continue
            if v == self.ap.get_default(k):
                continue
            self[k] = v
        
        
        return self