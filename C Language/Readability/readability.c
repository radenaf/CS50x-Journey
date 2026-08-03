#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int A = 65;
int a = 97;

int main(void)
{
    // Prompt user for text input
    string text = get_string("Text: ");

    int letters = 0;
    int words = 1; // Start with 1 to account for the last word
    int sentences = 0;
    // Count the number of letters, words, and sentences in the text
    for (int i = 0; i < strlen(text); i++)
    {
        // Count letters
        if (isalpha(text[i]))
        {
            letters++;
        }
        // Count words
        else if (isspace(text[i]))
        {
            words++;
        }
        // Count sentences
        else if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            sentences++;
        }
    }

    float L = letters / (float) words * 100;
    float S = sentences / (float) words * 100;
    int index = round(0.0588 * L - 0.296 * S - 15.8);

    // Grade the text based on the Coleman-Liau index
    if (index < 1)
    {
        printf("Before Grade 1\n");
    }

    else if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", index);



    }
}


