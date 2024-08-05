# Inequality Checker

Takes a list of inequalities as input.
Checks whether the inequalities are valid or not.
Outputs their normalized form.

## Example

```
$ cat input.txt
x ≤ y ≤ z ≤ x
x < a
a = b
b ≤ c
$ python3 ineqCheck.py input.txt
x = y = z < a = b
a = b ≤ c
```
