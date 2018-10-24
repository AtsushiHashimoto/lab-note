
# coding: utf-8

# # python compatible autoreload

# In[2]:



from IPython import get_ipython
ipython = get_ipython()
if '__IPYTHON__' in globals():
    ipython.magic('load_ext autoreload')
    ipython.magic('autoreload 2')


# # import your original modules
# !! Not use 'from xxx import func.' This disable lab-note to save your original modules automatically. 

# In[3]:


import labnote as ln


# # Python/Jupyter compatible argument parser

# In[4]:


parser = ln.ArgumentParser(description='This script is a demo of lab-note.')

parser.add_argument('path_root_src',         action='store',         nargs=None,         const=None,         default=None,         type=str,         choices=None,         help='Directory path where your taken photo files are located.',         metavar=None)


# # magics to make the code jupyter/python compatible

# In[5]:


args = None
script_name = None
if ln.utils.is_executed_on_ipython():
    args = ['path/to/foo']
    script_name = "examples.ipynb" # necessary only with password-authentifying jupyter.


# # parse arguments and set the parameter to Note.

# In[6]:


params = parser.parse_args(args)
note = ln.Note('./exp_log',script_name=script_name)
note.set_params(params)


# # save parameters before starting your experiment.

# In[7]:


note.save("Memo: this is a perfect experimental setting!")


# # save experimental results safely
# 'note.record()' makes result directory with timestamp.

# In[8]:


import os.path
with note.record() as dst_dir:
    print(dst_dir)
    with open(os.path.join(dst_dir,"test.txt"),'w') as f:
        f.write("a great result!!\n")


# # close session
# exit() calls note destructor, which save the jupyter log as an .html file in the `exp_log' directory.

# In[11]:


exit()
#note.wrapup()

