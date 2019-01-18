# class Note
<div style="text-align: right">
[[code](https://github.com/AtsushiHashimoto/lab-note/blob/c8c1a1fc4df8ac0e5cbccf4e1aa2a93c8099d6f2/labnote/core.py#L19)]</div>
Note records your experimental parameters, results, and note into a timestamped directly safely.

## Note()
Initialize Note class instance.

- arguments: log_dir, arguments, description, use_subdir, script_name

    note = Note(log_dir='./outputs',arguments='default_arguments.yaml')

### log_dir
Direct a directory in which all things are archived.

### arguments (optional)
Direct yaml file in which information for argument parser is written.
In that, keys are valuable name, and values are arguments passed to parser.add_argument function.
This is compatible with jupyter-notebook.

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

### description (default: None)
Comments that explains your code. This will appear in --help usage and memo.txt file in archive.

### use_subdir (default: False)
If use_subdir=True, every execution create archive subdirectory with timestamp.

### script_name (default: None)
You can change archived main script filename.


## Note.params
Access to configures attribute parameters.
Let assume the following config file ('argument_settings.yaml') exists.

    foo: 123

You can access the value of 'foo' by...

    >>> note = labnote.Note(arguments='argument_settings.yaml')
    >>> print(note.params.foo)
    123

## Note.save([memo=str])
save the main script, your original modules, and all parameters to a timestamped directly.
The timestamp is generated in the constructor.

## Note.record()
generate a timestamped directory, which is used to store all experimental results at a trial.
The timestamp is generated in this function call.

    with note.record() as rec:
      with open(rec.getpath('results.txt')) as f:
        f.write(<<your_precious_result>>)
