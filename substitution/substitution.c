#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])
{
    //Validate the line of code

        //Validate if its a single command line argument
        if (argc != 2)
        {
            printf("Usage: ./substitution key\n");
            return 1;
        }

        //Validate if the key is 26 characters long
        if (strlen(argv[1]) != 26)
        {
            printf("Insert 26 characters.\n");
            return 1;
        }
        //Validate if the key contains only alphabetic characters
        for (int i = 0, n = strlen(argv[1]); i < n; i++)
        {
            if (!isalpha(argv[1][i]))
            {
                printf("Key must only contain alphabetic characters.\n");
                return 1;
            }

            for (int j = i+1; j < n; j++)
            {
                if (tolower(argv[1][i])== tolower(argv[1][j]))
                {
                    printf("There should be no duplicate alphabets.\n");
                    return 1;
                }
            }

    }

    string key = argv[1];

    //Input from user (plaintex)
    string plain = get_string("plaintext: ");

    //Print ciphertext
    printf("ciphertext: ");
    for (int i = 0, n = strlen(plain); i < n; i++)
    {
        if (isalpha(plain[i]))
        {
            if (isupper(plain[i]))
            {
                printf("%c", toupper(key[plain[i] - 'A']));
            }
            else
            {
                printf("%c", tolower(key[plain[i] - 'a']));
            }
        }
        else
        {
            printf("%c", plain[i]);

        }
    }
printf("\n");

}

