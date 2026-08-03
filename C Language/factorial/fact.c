#include <stdio.h>
#include <cs50.h>

int factorial(int n);

int main(void)
{
    int n = get_int("Factorial of: ");
    printf("Factorial of %i is %i\n", n, factorial(n));
}

int factorial(int n)
{
    //Base case
    if (n == 0)
    {
        return 1;
    }

    //Recursive case
    return n * factorial(n - 1);
}
