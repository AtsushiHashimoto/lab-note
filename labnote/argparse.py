from warnings import warn
from easydict import EasyDict as edict
import labnote.utils as utils
import sys
import argparse as ap
class ArgumentParser(ap.ArgumentParser):
    '''
    ipythonとpytho環境の両方で動くプログラムのパラメタ管理システム．    
    優先順位: arg_parserのdefault値 < config_fileの値  < parse_argsのkwargsによる指定値 < コマンドラインの設定値
    '''
    def __init__(
        self,
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=[],
        formatter_class=ap.HelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True,
        allow_abbrev=True):

        super(ArgumentParser,self).__init__(prog=prog, usage=usage, description=description,
                                epilog=epilog,parents=parents,formatter_class=formatter_class,
                                prefix_chars=prefix_chars,
                                fromfile_prefix_chars=fromfile_prefix_chars,
                                argument_default=argument_default,
                                conflict_handler=conflict_handler,
                                add_help=add_help,allow_abbrev=allow_abbrev)
        
        self.required = set()


    def add_argument(self,*args,**kwargs):
        store_action = super(ArgumentParser,self).add_argument(*args,**kwargs)
        if len(store_action.option_strings)==0:
            # 必須項目
            self.required.add(store_action.dest)            
        return store_action  

    def is_registered(self,option_string):        
        for act in self._actions:
            if option_string in act.option_strings:
                return True
        return False

    def parse_args(self,args=None,namespace=None):
        if not self.is_registered('--config'):
            if self.is_registered('-c'):
                self.add_argument('--config',nargs='+',default=None,help='load a yaml config file.')
            else:
                self.add_argument('--config','-c',nargs='+',default=None,help='load a yaml config file.')
        if not self.is_registered('--output'):
            if self.is_registered('-o'):
                self.add_argument('--output',nargs=1,default=None,help='set the output directory.')
            else:
                self.add_argument('--output','-o',nargs=1,default=None,help='load a yaml config file.')

        if utils.is_executed_on_ipython():
            # 引数をtempに退避
            temp = sys.argv
            sys.argv = sys.argv[:1]
            # 必須項目がkwargsに存在するか確認
            if len(self.required)>0:
                if args is None or len(args) != len(self.required):
                    req_args = "[%s]"%", ".join(["%s"%d for d in self.required])
                    raise RuntimeError("A required parameter is not given to parse_args.\n"+ \
                                        "ex) parse_args(args=%s)"%req_args)
                    
        params = super(ArgumentParser,self).parse_args(args,namespace)

        if utils.is_executed_on_ipython():
            # 引数を戻しておく
            sys.argv=temp   
        params = edict(params.__dict__)
        return params