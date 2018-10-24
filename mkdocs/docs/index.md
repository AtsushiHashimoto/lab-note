## Accellarate your python experiments with Lab-Note!

Lab-Note is a toolkit for experiments written in python language. It was developped to make your experimental trials recodable and reproducible.

## Quick Start

### Install
  %pip install git+https://github.com/AtsushiHashimoto/lab-note.git

### How to use?
  - [sample code](https://github.com/AtsushiHashimoto/lab-note/blob/master/examples.ipynb)


## Archive
This toolkit archive experiment in a timestamped directory, which consists of...

 - params.yaml (all parameters of the experiment)
 - &lt;&lt; script_name&gt;&gt; (main script of the experiment)
 - &lt;&lt; modules &gt;&gt; (all imported modules under the main script's directory.)
 - results (all experimental results)
 - memo.txt (optional. A message hard-coded in the experiment.)
 - note.pickle (pickled parameters to reproduce the experiments.)

## Reproduce the experiment.
 move to the archive directory, then run the main script.

## Supported Environment
Lab note is currently tested on:

 - Python 3.6.5
 - Jupyter 5.4.1 (best with token authentification or no authentification.)
