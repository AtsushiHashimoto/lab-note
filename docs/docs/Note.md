# class Note
Note records your experimental parameters, results, and note into a timestamped directly safely.


## Note.set_params(dict)
set parameters related to your experiments.

## Note.save()
save the main script, your original modules, and all parameters to a timestamped directly.
The timestamp is generated in the constructor.

## Note.record()
generate a timestamped directory, which is used to store all experimental results at a trial.
The timestamp is generated in this function call.
