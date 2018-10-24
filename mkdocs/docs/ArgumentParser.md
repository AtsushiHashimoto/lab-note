# class ArgumentParser
<div style="text-align: right"> [[code](https://github.com/AtsushiHashimoto/lab-note/blob/c8c1a1fc4df8ac0e5cbccf4e1aa2a93c8099d6f2/labnote/argparse.py#L6)]
</div>
ArgumentParser is a python/jupyter compatible argument parser.

## functions
The class has constructor, 'add_argument' and 'parse_arg'.
The interfaces of all functions are the same with argparse.ArgumentParser.

# Example: convert your ArgmentParser jupyter-compatible.

You need only commenting out built-in argparse, and import labnote.Argumentparser.

```
    #from argparse import ArgumentParser # <- comment out!
    from lab-note import ArgumentParser # <- add this line!

    parser = ArgumentParser
    parser.add_argument('path_root_src', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where your taken photo files are located.', \
        metavar=None)
    parser.add_argument('--param1', \
        action='store', \
        nargs=None, \
        const=None, \
        default=1.0, \
        type=float, \
        choices=None, \
        help='A optional parameter.', \
        metavar=None)

    params = parser.parse_args()
    print(params)
```
