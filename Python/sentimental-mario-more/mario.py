
# Get pyramid height from user
while True:
    try:
        height = int(input("Height: "))
    except ValueError:
        print("Height must be an integer.")
        continue

    if height < 1 or height > 8:
        print("Height must be between 1 and 8.")
        continue
    
    break

# Print both sides of pyramid with a space in between
for i in range(1, height + 1):
    # Print left side of pyramid
    print(" " * (height - i) + "#" * i, end="")

    # Print space between pyramids
    print("  ", end="")

    # Print right side of pyramid
    print("#" * i)




