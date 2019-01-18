## Accellarate your python experiments with Lab-Note!

Lab-Note is a toolkit for experiments written in python language. It was developed to make your experimental trials recordable, reproducible, and configurable.

## Quick Start

### Install
    % pip install git+https://github.com/AtsushiHashimoto/lab-note.git

### How to use?
  - [sample code](https://github.com/AtsushiHashimoto/lab-note/blob/master/examples_exp.ipynb)


## Archive
This toolkit archive experiments in a directory with its configuration.
The archive consists of...

 - params.yaml (all parameters of the experiment)
 - &lt;&lt;script_name&gt;&gt; (main script of the experiment)
 - &lt;&lt;modules&gt;&gt; (all imported modules under the main script's directory.)
 - &lt;&lt;results&gt;&gt; (all experimental results)
 - memo.txt (optional)

## Reproduce the experiment.
 move to the archive directory, and type...

    % python <<script_name>>

## Supported Environment
Lab note is currently tested on:

 - Python 3.6.5
 - Jupyter 5.4.1 (best with token authentification or no authentification.)
