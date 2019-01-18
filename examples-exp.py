
# coding: utf-8

# # 1. import your original modules
# !! Not use 'from xxx import func.' This disable lab-note to save your original modules automatically. 

# In[1]:


# coding=utf-8
#import my_precious_module #<- your module files/directories must be placed under the current directly.

import labnote as lb


# # 2. load yaml for argument setting
# The following configuration is equivalent to write...
# 
#     parser.add_argument('--N',default=100,type=int,help='# of samples')
#     parser.add_argument('--alpha', '-a', default=1.0,type=float,help='std. dev. of the first normal distribution')
#     parser.add_argument('--beta', '-b', default=1.0, type=float,help='std. dev. of the second normal distribution')
# 

# In[2]:


import yaml
from labnote.utils import register_arg4yaml as reg

default_args_yaml = './example_default_args.yml'
# all options of add_argument function can be a key of each parameter entry.
with open(default_args_yaml,'w') as f:
    conf = '''
N:
  default: 100
  type: int
  help: '# of samples'
alpha:
  name: -a
  default: 1.0
  type: float
  help: std. dev. of the first normal distribution
beta:
  name: -b
  default: 1.0
  type: float
  help: std. dev. of the second normal distribution
'''
    f.write(conf)


# # 3. Feed yaml from command line
# The following configuration can be fed to your code by...
# 
#     % python your_code.py --config ./test.yml
#     
# And it is equivalent, in this case, to...
# 
#     % python your_code.py --alpha 2.0 --beta 0.5 

# In[3]:


config_yaml = './test.yml'
with open(config_yaml,'w') as f:
    f.write(
'''
alpha: 2.0
beta: 0.5
'''
)


# # 4. Create a note.

# In[4]:


note = lb.Note('./log',arguments=[default_args_yaml])
print(note.params)


# ### simulate a process call with --config option.
# 
#     % python your_code.py --config ./test.yml

# In[5]:


note = lb.Note('./log',arguments=[default_args_yaml,{'config':config_yaml}])
print(note.params)


# # 5. Save experimental results (in two ways)
# 'note.record()' makes result directory with timestamp.

# In[6]:


import os.path
import numpy as np
from numpy.random import randn


with note.record() as rec:
    print(rec.dirname)
    x1 = randn(note.params.N)*note.params.alpha
    x2 = randn(note.params.N)*note.params.beta
    x = x1+x2
    ideal_sigma = np.sqrt(note.params.alpha**2 + note.params.beta**2)
    real_sigma = np.sqrt(np.var(x))
    rec.timestamp('Record timestamp here')
    with open(rec.getpath("test.txt"),'w') as f:
        f.write("ideal_sigma: %f\n"%ideal_sigma)
        f.write("real_sigma: %f\n"%real_sigma)
    last_exp_log = rec.dirname

# The above code can be replaced to the following style.
rec = note.record()
# rec.open()
# ...
# rec.close()


# # 6. close session
# exit() calls note destructor, which save the jupyter log as an .html file in the `exp_log' directory.

# In[7]:


note.wrapup()
exit()

