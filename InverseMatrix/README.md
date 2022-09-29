## inverse

It calculate the inverse of square matrix using Gaussian elimination and LU factorization.
It apply [partial pivoting](https://www2.math.upenn.edu/~kazdan/320F18/Notes/Gauss-Elim/LU-P.html). You can watch the result of each step of calculation.
Finally the program display inverse matrix, LU matrix.
With command line options, you can supress other result and display only inverse matrix.
It can receive data of input matrix from a file or a stream.

```

> forward elimination
>
> 2.0 1.0 1.0 0.0
> 4.0 3.0 3.0 1.0
> 8.0 7.0 9.0 5.0
> 6.0 7.0 9.0 8.0
>
> pivot (1,1):
>
> swap row 1 <-> 3
>
> Row(2) - (4)\*Row(1)
>
> Row(3) - (2)\*Row(1)
>
> Row(4) - (6)\*Row(1)
>
> A :
>
> 1.0 0.875 1.125 0.625
> 0.0 -0.5 -1.5 -1.5
> 0.0 -0.75 -1.25 -1.25
> 0.0 1.75 2.25 4.25
>
> LU :
>
> 8.0 7.0 9.0 5.0
> 0.5 1.0 0.0 0.0
> 0.25 0.0 0.0 0.0
> 0.75 0.0 0.0 1.0
>
> pivot (2,2):
>
> swap row 2 <-> 4
>
> Row(3) - (-0.75)\*Row(2)
>
> Row(4) - (-0.5)\*Row(2)
>
> A :
>
> 1.0 0.875 1.125 0.625
> 0.0 1.0 1.286 2.429
> 0.0 0.0 -0.286 0.571
> 0.0 0.0 -0.857 -0.286
>
> LU :
>
> 8.0 7.0 9.0 5.0
> 0.75 1.75 2.25 4.25
> 0.25 -0.429 0.0 0.0
> 0.5 -0.286 0.0 0.0
>
> pivot (3,3):
>
> swap row 3 <-> 4
>
> Row(4) - (-0.285714)\*Row(3)
>
> A :
>
> 1.0 0.875 1.125 0.625
> 0.0 1.0 1.286 2.429
> 0.0 0.0 1.0 0.333
> 0.0 0.0 0.0 0.667
>
> LU :
>
> 8.0 7.0 9.0 5.0
> 0.75 1.75 2.25 4.25
> 0.5 -0.286 -0.857 -0.286
> 0.25 -0.429 0.333 0.0
>
> square matrix - inversiable
>
> A :
>
> 1.0 0.875 1.125 0.625
> 0.0 1.0 1.286 2.429
> 0.0 0.0 1.0 0.333
> 0.0 0.0 0.0 0.667
>
> LU :
>
> 8.0 7.0 9.0 5.0
> 0.75 1.75 2.25 4.25
> 0.5 -0.286 -0.857 -0.286
> 0.25 -0.429 0.333 0.667
>
> true
>
> backward elimination
>
> pivot (4,4):
>
> Row(3) - (0.333333)\*Row(4)
>
> Row(2) - (2.42857)\*Row(4)
>
> Row(1) - (0.625)\*Row(4)
>
> 1.0 0.875 1.125 0.0
> 0.0 1.0 1.286 0.0
> 0.0 0.0 1.0 0.0
> 0.0 0.0 0.0 1.0
>
> pivot (3,3):
>
> Row(2) - (1.28571)\*Row(3)
>
> Row(1) - (1.125)\*Row(3)
>
> 1.0 0.875 0.0 0.0
> 0.0 1.0 0.0 0.0
> 0.0 0.0 1.0 0.0
> 0.0 0.0 0.0 1.0
>
> pivot (2,2):
>
> Row(1) - (0.875)\*Row(2)
>
> 1.0 0.0 0.0 0.0
> 0.0 1.0 0.0 0.0
> 0.0 0.0 1.0 0.0
> 0.0 0.0 0.0 1.0
>
> pivot (1,1):
>
> true
>
> 1.0 0.0 0.0 0.0
> 0.0 1.0 0.0 0.0
> 0.0 0.0 1.0 0.0
> 0.0 0.0 0.0 1.0
>
> Inverse matrix (by gauss Jordan)
>
> 2.25 -0.75 -0.25 0.25
> -3.0 2.5 -0.5 -2.22e-16
> -0.5 -1.0 1.0 -0.5
> 1.5 -0.5 -0.5 0.5
>
> LU matrix
>
> 8.0 7.0 9.0 5.0
> 0.75 1.75 2.25 4.25
> 0.5 -0.286 -0.857 -0.286
> 0.25 -0.429 0.333 0.667
>
> permutation matrix
>
> [4](2,3,3,3)
>
> inverse matrix (by LU)
>
> 2.25 -0.75 -0.25 0.25
> -3.0 2.5 -0.5 -3.806e-16
> -0.5 -1.0 1.0 -0.5
> 1.5 -0.5 -0.5 0.5
```

## Prerequisites

- Flex and Bison
- Boost library

## Format of matrix

- basic format

  ```
  2, 1, 1, 0
  4, 3, 3, 1
  8, 7, 9, 5
  6, 7, 9, 8
  ```

- you can use basic algebra expression. The program also provide basic math function and constant.
  ```
  t=2*%pi*30/360
  cos(t), sin(t)\*%e
  3+2^7+(3+2), 77
  ```

## Usage

```
Usage: inverse [option] [file]

option:
--help, --level=#NUM(0-3)

file format:
exp ,exp .. ,exp
...
exp ,exp .. ,exp

ex):
2*3, 7*sqrt(9)
2^2, -(8+9)^2
❯ cat data2 | ./inverse
❯ ./inverse --level=2 data2
```
