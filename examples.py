
# coding: utf-8

# # import your original modules
# !! Not use 'from xxx import func.' This disable lab-note to save your original modules automatically. 

# In[1]:


# coding=utf-8
#import my_precious_module #<- your module files/directories must be placed under the current directly.

import labnote as lb


# # Python/Jupyter compatible argument parser

# In[2]:


parser = lb.ArgumentParser(description='This script is a demo of lab-note. Calculate std. dev. of a distribution obtained by sum of two normal dist N(0,alpha),N(0,beta).')

parser.add_argument('alpha',         type=float,         help='std. dev. of the first normal distribution')
parser.add_argument('--beta',         type=float,         default=1.0,
        help='std. dev. of the second normal distribution')
parser.add_argument('-N', '--N',        type=int,         default=100,
        help='# of samples')


# # magics to make the code jupyter/python compatible

# In[3]:


args = None
script_name = None

if lb.utils.is_executed_on_ipython():
    args = ['1.0'] #<- to emurate command line option, values must be given as str type values.
    script_name = "examples.ipynb" # necessary only with password-authentifying jupyter.


# # parse arguments and set the parameter to Note.

# In[4]:


note = lb.Note('./exp_log',
               safe_mode=False, # set False during debugging.
               script_name=script_name)
params = parser.parse_args(args)
note.set_params(params)


# # save parameters before starting your experiment.

# In[5]:


note.save("Memo: this is a perfect experimental setting!")


# # save experimental results safely (in two ways)
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


# # show records

# In[7]:


print('test.txt (calculation result)')
print('---------------')
with open(os.path.join(last_exp_log,'test.txt')) as f:
    for l in f:
        print(l)
print('---------------')


# In[8]:


print('timestamp')
print('---------------')
with open(os.path.join(last_exp_log,'timestamp')) as f:
    for l in f:
        print(l)
print('---------------')


# In[9]:


print('requirements.txt')
print('---------------')
with open(os.path.join(note.makedirs(),'requirements.txt')) as f:
    for l in f:
        print(l)
print('---------------')


# # close session
# exit() calls note destructor, which save the jupyter log as an .html file in the `exp_log' directory.

# In[ ]:


#note.wrapup()
#exit()

