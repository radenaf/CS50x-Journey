import csv
import sys


def main():

    # TODO: Check for command-line usage
    argv = sys.argv
    if len(argv) != 3:

        sys.exit("Usage: python dna.py data.csv sequence.txt")

    # TODO: Read database file into a variable
    with open(argv[1], "r") as DBSfile:
        reader = csv.DictReader(DBSfile)
        database = [row for row in reader]

    # TODO: Read DNA sequence file into a variable
    with open(argv[2], "r") as DNAfile:
        sequence = DNAfile.read()

    # TODO: Find longest match of each STR in DNA sequence
    str_counts = {}
    for key in database[0].keys():
        if key == "name":
            continue
        str_counts[key] = longest_match(sequence, key)

    # TODO: Check database for matching profiles
    for row in database:
        match = True
        for key in str_counts.keys():
            if str_counts[key] != int(row[key]):
                match = False
                break
        if match:
            print(row["name"])
            return
    print("No match")


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in sequence, return longest run found
    return longest_run


main()
