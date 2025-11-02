# Beautiful XOR

**Time Limit:** 2 seconds
**Memory Limit:** 256 megabytes

## Statement

You are given two integers $$$a$$$ and $$$b$$$. You are allowed to perform the following operation any number of times (including zero):
choose any integer $$$x$$$ such that $$$0 \le x \le a$$$ (the current value of $$$a$$$, not initial),
set $$$a := a \oplus x$$$. Here, $$$\oplus$$$ represents the
bitwise XOR
operator.
After performing a sequence of operations, you want the value of $$$a$$$ to become exactly $$$b$$$.
Find a sequence of at most $$$100$$$ operations (values of $$$x$$$ used in each operation) that transforms $$$a$$$ into $$$b$$$, or report that it is impossible.
Note that you are not required to find the minimum number of operations, but any valid sequence of at most $$$100$$$ operations.

## Input

The first line of input contains a single integer $$$t$$$ ($$$1 \le t \le 1000$$$) — the number of test cases.
Each test case contains two integers $$$a$$$ and $$$b$$$ ($$$1 \le a, b \le 10^9$$$).

## Output

For each test case, if it is impossible to obtain $$$b$$$ from $$$a$$$ using the allowed operations, print a single line containing $$$-1$$$.
Otherwise, on the first line print a single integer $$$k$$$ ($$$0 \le k \le 100$$$) — the number of operations. On the second line print $$$k$$$ integers ($$$x_1, x_2, \dots , x_k$$$) — the chosen values of $$$x$$$ in the order you apply them.
If there are multiple valid sequences, you may print any one of them.

## Note

For the first test case,
choose $$$x = 7$$$, now $$$a$$$ becomes equal to $$$9 \oplus 7 = 14$$$.
choose $$$x = 8$$$, now $$$a$$$ becomes equal to $$$14 \oplus 8 = 6$$$.
Thus, we can make $$$a = b$$$.
For the fourth test case, choosing $$$x = 5$$$ makes $$$a = b$$$.
