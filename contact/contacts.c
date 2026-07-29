#include <stdio.h>
#include <cs50.h>

int main (void)
{
    string name = get_string("What is your name? ");
    int age = get_int("What is your age? ");
    int phone = get_int("What is your phone number? ");
    int height = get_int("What is your height? ");
    printf("Name: %s\n", name);
    printf("Age: %d\n", age);
    printf("Phone: %d\n", phone);
    printf("Height: %d\n", height);

}
