#include <stdio.h>
#include <cs50.h>
#include <string.h>


int main(int argc, string argv[])
{

    if (argc < 2)
    {
        printf("Usage: ./initials name\n");
        return 1;
    }

    for(int i = 1; i < argc; i++)
    {
        printf("%c", argv[i][0]);

    }
    printf("\n");
}
