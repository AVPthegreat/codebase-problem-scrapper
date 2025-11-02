# Beautiful String

**Time Limit:** 1 second
**Memory Limit:** 256 megabytes

## Statement

You are given a binary$$$^{\text{∗}}$$$ string $$$s$$$ of length $$$n$$$.
Your task is to find any subsequence$$$^{\text{†}}$$$ $$$p$$$ of $$$s$$$ such that:
The subsequence $$$p$$$ is
non-decreasing
. That is, each character in $$$p$$$ is not greater than the next one.
Let $$$x$$$ denote the string obtained by
removing all characters of $$$p$$$ from $$$s$$$
, while preserving the order of the remaining characters. Then $$$x$$$ must be a
palindrome
$$$^{\text{‡}}$$$.
You only need to output any valid subsequence $$$p$$$ that satisfies both conditions. If no such subsequence exists, output $$$-1$$$.
Note that an empty string is both non-decreasing and a palindrome.
$$$^{\text{∗}}$$$A binary string is a string consisting of characters '
0
' and '
1
'.
$$$^{\text{†}}$$$A
subsequence
of a string $$$s = s_1s_2\ldots s_n$$$ is a sequence $$$p = s_{i_1}s_{i_2}\ldots s_{i_k}$$$ such that $$$1 \leq i_1 < i_2 < \ldots < i_k \leq n$$$. The characters are selected in order, but not necessarily contiguously. Note that an empty string is a subsequence of any string.
$$$^{\text{‡}}$$$A string $$$t = t_1t_2\ldots t_m$$$ is a
palindrome
if $$$t_i = t_{m - i + 1}$$$ for all $$$1 \leq i \leq m$$$. In other words, the string reads the same forward and backward.

## Input

The first line contains a single integer $$$t$$$ ($$$1 \le t \le 3000$$$) — the number of test cases.
The first line of each test case contains a single integer $$$n$$$ ($$$1 \le n \le 10$$$) — the length of the string.
The second line contains a binary string $$$s$$$ of length $$$n$$$.

## Output

If a solution exists:
On the first line, print a single integer $$$k$$$ ($$$0 \le k \le n$$$) — the length of the subsequence $$$p$$$.
On the second line, print $$$k$$$ distinct integers $$$i_1, i_2, \dots, i_k$$$ ($$$1 \le i_1 < i_2 < \dots < i_k \le n$$$) — the indices of the characters in $$$s$$$ that form $$$p$$$ (in order as they appear in $$$s$$$).
Otherwise, print a single line containing $$$-1$$$.

## Note

In the first test case, we remove an empty string, resulting in $$$x = \texttt{010}$$$, which is a palindrome.
In the second test case, we remove $$$p = \texttt{01}$$$ (indices $$$2$$$, $$$3$$$), resulting in $$$x = \texttt{0}$$$, which is a palindrome.
In the third test case, we remove $$$p = \texttt{00111}$$$ (indices $$$1$$$ to $$$5$$$), resulting in an empty string, which is trivially a palindrome.
In the fourth test case, we remove $$$p = \texttt{01}$$$ (indices $$$3$$$, $$$4$$$), resulting in $$$x = \texttt{110011}$$$, which is a palindrome.
In the fifth test case, we remove $$$p = \texttt{01}$$$ (indices $$$5$$$, $$$6$$$), resulting in $$$x = \texttt{1001}$$$, which is a palindrome.
