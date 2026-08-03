#include <stdio.h>
#include <cs50.h>
#include <stdlib.h>

typedef struct node
{
    int number;
    struct node *next;
} node;

int main(void)
{
    node *list = NULL;

    for (int i = 0; i < 3; i++)
    {
        int x = get_int("Number: ");

        node *n = malloc(sizeof(node));
        n -> number = x;
        n -> next = list;

        list = n;

    }

    for (node *ptr = list; ptr != NULL; ptr = ptr -> next)
    {
        printf("%i\n", ptr -> number);
    }


    // Free memory
    node *ptr = list;
    while (ptr != NULL)
    {
        node *tmp = ptr;
        ptr = ptr -> next;
        free(tmp);
    }
}
