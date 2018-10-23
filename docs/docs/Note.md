# class Note

Note records your experimental parameters, results, and note into a timestamped directly safely.

## set_params(dict)

## save()

## get_result_file():

    with note.get_result_file() as f:
        save_your_result(f)


## get_result_dir()

    with note.get_result_dir() as dir:
        with open("%s/result.csv"%dir,'w') as f:
            save_your_result(f)
        with open("%s/result.json"%dir,'w') as f:
            save_your_reulst2(f)

