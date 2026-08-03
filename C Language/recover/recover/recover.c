#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


int main(int argc, char *argv[])
{
    // Accept a single command-line argument
    if (argc != 2)
    {
        printf("Usage: ./recover FILE\n");
        return 1;
    }

    // Open the memory card
    FILE *raw_file = fopen(argv[1], "rb");

    // Create a buffer for a block of data
    uint8_t buffer[512];
    int found_jpeg = 1;
    int counter = 0;
    char filename[8];
    FILE *img = NULL;

    // While there's still data left to read from the memory card
    while (fread(buffer, 1, 512, raw_file) == 512)
    {
        // Create JPEGs from the data
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // Create a new JPEG file
            found_jpeg = 0;

        }
        if (found_jpeg == 0)
        {
            if (counter != 0)
            {
                fclose(img);
            }
            sprintf(filename, "%03i.jpg", counter);

            counter ++;

            img = fopen(filename, "wb");
            fwrite(buffer, 1, 512, img);

            found_jpeg = 1;
        }
        else if(counter != 0)
        {
            fwrite(buffer, 1, 512, img);
        }
    }

    // Close the files
    if (img != NULL)
    {
        fclose(img);
    }
    fclose(raw_file);

    return 0;
}
