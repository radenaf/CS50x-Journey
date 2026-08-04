
A = 65
a = 97

text = input("Text: ")

# Count letters, words, and sentences in the text
letter_count = 0
word_count = 1  # Start with 1 to account for the first word
sentence_count = 0

for char in text:
    if char.isalpha():
        letter_count += 1
    elif char.isspace():
        word_count += 1
    elif char in ['.', '!', '?']:
        sentence_count += 1

# Calculate the Coleman-Liau index

L = (letter_count / word_count) * 100
S = (sentence_count / word_count) * 100
index = 0.0588 * L - 0.296 * S - 15.8
round_index = round(index)

# Print the grade level based on the index
if round_index < 1:
    print("Before Grade 1")
elif round_index >= 16:
    print("Grade 16+")
else:
    print(f"Grade {round_index}")
