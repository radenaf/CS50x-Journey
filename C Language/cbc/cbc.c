#include <stdio.h>
#include <cs50.h>
#include <string.h>

int main(void)
{
    string text = get_string( "Input: " );

    for (int i = 0, n = strlen(text); i < n; i++)
    {
        printf("%c", text[i]);
    }
printf("\n");

}
