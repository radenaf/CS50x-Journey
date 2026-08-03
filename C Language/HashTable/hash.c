#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>

int hash (char *word);

int main(void)
{
    // Prompt user for a string
    char *word = get_string("Word: ");

    // Print the string
    printf("Hash Value: %i\n", hash(word));
}

int hash (char *word)
{

    // A -> 0

    if (word == NULL || strlen(word) < 2)
    {
        return -2;
    }
    char c = word[0];
    char c1 = word[1];
    if (isalpha(c) && isalpha(c1))
    {
        c = toupper(c);
        c1 = toupper(c1);
        return (c - 'A') * 100 + c1 - 'A';
    }
    return -1;

}
