# Distinct Elements

**Time Limit:** 1.5 seconds
**Memory Limit:** 256 megabytes

## Statement

Given an array $$$c$$$, let $$$f(c)$$$ be the number of distinct elements in $$$c$$$. For example, $$$f([1,2,2])=2$$$ because there are two distinct elements in $$$[1,2,2]$$$: $$$1$$$ and $$$2$$$. Also, define $$$c[i,j]$$$ as the subarray$$$^{\text{∗}}$$$ of $$$c$$$ bounded by positions $$$i$$$ and $$$j$$$ (that is, the array $$$[c_i,c_{i+1},\ldots,c_j]$$$).
There is an array $$$a$$$ of size $$$n$$$. An array $$$b$$$ of $$$n$$$ elements is constructed such that $$$b_i=f(a[1,i])+f(a[2,i])+\ldots+f(a[i,i])$$$. You are given the array $$$b$$$. Find any possible $$$a$$$ with elements $$$1 \leq a_i \leq n$$$. It is guaranteed that at least one possible $$$a$$$ exists.
$$$^{\text{∗}}$$$An array $$$x$$$ is a subarray of an array $$$y$$$ if $$$x$$$ can be obtained from $$$y$$$ by the deletion of several (possibly, zero or all) elements from the beginning and several (possibly, zero or all) elements from the end.

## Input

Each test contains multiple test cases. The first line contains the number of test cases $$$t$$$ ($$$1 \le t \le 10^4$$$). The description of the test cases follows.
The first line of each test case contains an integer $$$n$$$ ($$$1 \leq n \leq 10^5$$$) – the number of elements in $$$a$$$ and $$$b$$$.
The second line of each test case contains $$$n$$$ integers $$$b_1,b_2,\ldots,b_n$$$ ($$$1 \leq b_i \leq 10^{18}$$$).
It is guaranteed that the sum of $$$n$$$ over all test cases does not exceed $$$10^5$$$.

## Output

For each test case, print any possible $$$a$$$ on a new line. The array $$$a$$$ should satisfy $$$1\leq a_i\leq n$$$.
For every test case, it is guaranteed at least one $$$a$$$ that satisfies the conditions exists.

## Note

Let's verify our output for the second test case is correct:
$$$b_1=f([2])=1$$$
$$$b_2=f([2,3])+f([3])=2+1=3$$$
$$$b_3=f([2,3,2])+f([3,2])+f([2])=2+2+1=5$$$
