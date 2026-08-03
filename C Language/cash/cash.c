#include <cs50.h>
#include <stdio.h>

int get_cents(void);

int main(void)
{
    // Prompt user for input
    int cents = get_cents();

    // Calculate the number of quarters
    int quarters = cents / 25;
    cents %= 25;

    // Calculate the number of dimes
    int dimes = cents / 10;
    cents %= 10;

    // Calculate the number of nickels
    int nickels = cents / 5;
    cents %= 5;

    // Calculate the number of pennies
    int pennies = cents;

    // Sum up total number of coins
    int coins = quarters + dimes + nickels + pennies;

    // Print total number of coins
    printf("%i\n", coins);

    return 0;
}

int get_cents(void)
{
    int cents;

    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);

    return cents;
}
