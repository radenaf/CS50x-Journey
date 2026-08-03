#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


char *concat(char *s1, char *s2);

int main(void)
{
    char *s1 = get_string("string 1: ");
    char *s2 = get_string("string 2: ");

    char *s3 = concat(s1, s2);
    printf ("%s\n", s3);
    free(s3);
}

char *concat(char *s1, char *s2)
{
    //Get memory for s3

    int len1 = strlen(s1);
    int len2 = strlen(s2);

    char *s3 = malloc(len1 + len2 + 1);



    //Copy values from s1 and s2 into s3
    for (int i = 0; i < len1; i++)
    {
        s3[i] = s1[i];
    }
    for (int i = 0; i < len2; i++)
    {
        s3[len1 + i] = s2[i];
    }
    s3[len1 + len2] = '\0';



    //Return s3
    return s3;
}
