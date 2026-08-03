#include <stdio.h>
#include <stdlib.h>
#include <cs50.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./pdf <filename>\n");
        return 1;
    }

    FILE *pdf = fopen(argv[1], "r");

    uint8_t buffer[4];

    uint8_t signature[] = {0x25, 0x50, 0x44, 0x46}; // PDF signature: %PDF

    fread(buffer, 1, 4, pdf);
    fclose(pdf);

    for (int i = 0; i < 4; i++)
    {
        if (buffer[i] != signature[i])
        {
            printf("Not a PDF file.\n");
            return 1;
        }
    }
    printf("PDF file detected.\n");
    return 0;
}

