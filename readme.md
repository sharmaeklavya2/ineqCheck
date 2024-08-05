# Inequality Checker

Takes a list of inequalities as input.
Checks whether the inequalities are consistent or not.
Outputs their normalized form.

## Example

```
$ cat input1.txt
x ≤ y ≤ z ≤ x
x < a
a = b
b ≤ c
$ python3 ineqCheck.py input1.txt
x = y = z < a = b
a = b ≤ c
inequalities are consistent
$ cat input2.txt
x ≤ y
x > y
$ python3 ineqCheck.py input2.txt
x = y
strictness violated for these inequalities:
x > y
```
