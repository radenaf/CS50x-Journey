#include <stdio.h>
#include <cs50.h>

int fib(int n);

int main(void)
{
    int n = get_int("Fibnacci number: ");
    printf("The %i Fibonacci number is %i\n", n, fib(n));
}

// Takes fibonacci number and returns the corresponding Fibonacci number
int fib(int n)
{
    // Base cases
    if (n == 0)
    {
        return 0;
    }
    if (n == 1)
    {
        return 1;
    }

    // Recursive case
    return fib(n - 1) + fib(n - 2);
}
