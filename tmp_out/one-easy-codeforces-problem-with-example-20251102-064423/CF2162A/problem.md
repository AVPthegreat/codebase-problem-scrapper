# Beautiful Average

**Time Limit:** 1 second
**Memory Limit:** 256 megabytes

## Statement

You are given an array $$$a$$$ of length $$$n$$$.
Your task is to find the maximum possible average value of any subarray$$$^{\text{∗}}$$$ of the array $$$a$$$.
Formally, for any indices $$$l, r$$$ such that $$$1 \le l \le r \le n$$$, define the average of the subarray $$$a_l, a_{l+1}, \dots, a_r$$$ as the sum of elements divided by the number of elements or: $$$$$$\texttt{avg}(l,r) = \frac{1}{r-l+1} \sum_{i=l}^{r} a_i$$$$$$ Output the maximum value of $$$\texttt{avg}(l,r)$$$ over all choices of $$$l, r$$$.
$$$^{\text{∗}}$$$An array $$$b$$$ is a subarray of an array $$$a$$$ if $$$b$$$ can be obtained from $$$a$$$ by deletion of several (possibly, zero or all) elements from the beginning and several (possibly, zero or all) elements from the end. In particular, an array is a subarray of itself.

## Input

The first line contains a single integer $$$t$$$ ($$$1 \le t \le 10^4$$$) — the number of test cases.
The first line of each testcase contains a single integer $$$n$$$ ($$$1 \le n \le 10$$$) — the length of the array $$$a$$$.
The second line of each testcase contains $$$n$$$ integers $$$a_1, a_2, \dots, a_n$$$ ($$$1 \le a_i \le 10$$$) — the elements of the array.

## Output

For each testcase, output a single integer — the maximum average of any subarray of the given array.
It can be shown that the answer is always an integer.
