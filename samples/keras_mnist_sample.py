
# coding: utf-8

# In[2]:


import labnote as lb
import os


# In[3]:


parser = lb.ArgumentParser()
parser.add_argument('epochs',type=int)
parser.add_argument('--batch_size',type=int,default=128)
parser.add_argument('--gpu_dev',type=str,default='0')

args = None
script_name=None  # <- required only for jupyter with password authentification
if lb.utils.is_executed_on_ipython():
    args = ['20']
    script_name = 'keras_mnist_sample.ipynb'

params = parser.parse_args(args=args)


# In[4]:


params.num_classes = 10
note = lb.Note('./log_dir',script_name=script_name)
note.set_params(params)


# In[7]:


os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
os.environ["CUDA_VISIBLE_DEVICES"] = note.params.gpu_dev


# In[8]:


'''Trains a simple deep NN on the MNIST dataset.
Gets to 98.40% test accuracy after 20 epochs
(there is *a lot* of margin for parameter tuning).
2 seconds per epoch on a K520 GPU.
'''

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint, CSVLogger


# In[9]:


# the data, split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, note.params.num_classes)
y_test = keras.utils.to_categorical(y_test, note.params.num_classes)

model = Sequential()
model.add(Dense(512, activation='relu', input_shape=(784,)))
model.add(Dropout(0.2))
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(note.params.num_classes, activation='softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=RMSprop(),
              metrics=['accuracy'])


# In[10]:


note.save(memo='sample code for keras mnist. I just want to explain how to use note with general deep learning framework.')


# In[11]:


with note.record() as rec:
    print(rec.dirname)
    csv_name = os.path.join(rec.dirname,"history.csv")
    model_name = os.path.join(rec.dirname,"mnist_models.pkl")
    cb_csv = CSVLogger(csv_name)
    cb_mcp = ModelCheckpoint(model_name,period=5)

    history = model.fit(x_train, y_train,
                    batch_size=note.params.batch_size,
                    epochs=note.params.epochs,
                    verbose=1,
                    validation_data=(x_test, y_test),
                    callbacks=[cb_csv,cb_mcp]
                       )
    score = model.evaluate(x_test, y_test, verbose=0)
    with open(os.path.join(rec.dirname,"score.txt"),'w') as f:
        f.write("Test loss: %f\n"%score[0])
        f.write("Test accuracy: %f\n"%score[1])
    last_exp = rec.dirname


# In[ ]:


with open(os.path.join(last_exp,"score.txt")) as f:
    for l in f:
        print(l)
exit()

