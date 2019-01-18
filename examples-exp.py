
# coding: utf-8

# # 1. import your original modules
# !! Not use 'from xxx import func.' This disable lab-note to save your original modules automatically. 

# In[1]:


# coding=utf-8
#import my_precious_module #<- your module files/directories must be placed under the current directly.

import labnote as lb


# # 2. load yaml for argument setting
# The following code is just to produce yaml in code. You can prepare it manually.

# In[2]:


import yaml
from labnote.utils import register_arg4yaml as reg
# Create an example of yaml to set command-line arguments.
# Any args for add_argument function is available.
# You can create the file by editting the yaml file directly.
default_args = {
    'alpha':reg(1.0,'-a',help='std. dev. of the first normal distribution'),
    'beta':reg(1.0,'-b',help='std. dev. of the second normal distribution'),
    'N':reg(100,'-N',int,help='# of samples'),    
}
default_args_yaml = './example_default_args.yml'

#with open(default_args_yaml,'w') as f:
#    f.write(yaml.dump(default_args, default_flow_style=False))


# ### example_default_args.yml
# 
#     N:
#       default: 100
#       help: '# of samples'
#       type: int
#     alpha:
#       default: 1.0
#       help: std. dev. of the first normal distribution
#       type: float
#     beta:
#       default: 1.0
#       help: std. dev. of the second normal distribution
#       type: float

# # 3. Feed yaml from command line
# The following code is just to produce config file in code. You can prepare it manually.
# To feed config file (from command line), use --config or -c option.

# In[3]:


# Create an example of an experimental configulation.
# You can create the file by editting the yaml file directly.
config_args = {
    'beta':0.5
}
config_yaml = './test.yml'
with open(config_yaml,'w') as f:
    f.write(yaml.dump(config_args, default_flow_style=False))


# # 4. Create a note.

# In[4]:


note = lb.Note('./log',arguments=[default_args_yaml,{'foo':1}])
print(note.params)


# # 5. Save experimental results (in two ways)
# 'note.record()' makes result directory with timestamp.

# In[5]:


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

# In[6]:


note.wrapup()
exit()

