def needleman_wunsch(seq1, seq2, match_reward=1, mismatch_penalty=-1, gap_penalty=-1):
    # 1. Setup the Grid
    # We add 1 to the lengths to account for the starting empty state
    rows, cols = len(seq1) + 1, len(seq2) + 1
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Fill the first row and column with accumulating gap penalties
    for i in range(rows): matrix[i][0] = i * gap_penalty
    for j in range(cols): matrix[0][j] = j * gap_penalty
        
    # 2. Fill the Matrix (The Dynamic Programming part)
    for i in range(1, rows):
        for j in range(1, cols):
            # Did the letters match?
            is_match = seq1[i-1] == seq2[j-1]
            diagonal_score = matrix[i-1][j-1] + (match_reward if is_match else mismatch_penalty)
            
            # Or did we introduce a gap?
            up_score = matrix[i-1][j] + gap_penalty
            left_score = matrix[i][j-1] + gap_penalty
            
            # The score for this cell is the best of those three options
            matrix[i][j] = max(diagonal_score, up_score, left_score)
            
    # 3. Traceback 
    # Start at the bottom-right of the grid and walk back to the top-left
    align1, align2 = "", ""
    i, j = len(seq1), len(seq2)
    
    while i > 0 and j > 0:
        current_score = matrix[i][j]
        diagonal_score = matrix[i-1][j-1]
        up_score = matrix[i-1][j]
        left_score = matrix[i][j-1]
        
        is_match = seq1[i-1] == seq2[j-1]
        
        # Did we arrive here from the diagonal?
        if current_score == diagonal_score + (match_reward if is_match else mismatch_penalty):
            align1 += seq1[i-1]
            align2 += seq2[j-1]
            i -= 1
            j -= 1
        # Or did we arrive from above? (Gap in sequence 2)
        elif current_score == up_score + gap_penalty:
            align1 += seq1[i-1]
            align2 += "-"
            i -= 1
        # Or did we arrive from the left? (Gap in sequence 1)
        else:
            align1 += "-"
            align2 += seq2[j-1]
            j -= 1
            
    # Finish up any remaining characters if we hit the edge of the grid
    while i > 0:
        align1 += seq1[i-1]
        align2 += "-"
        i -= 1
    while j > 0:
        align1 += "-"
        align2 += seq2[j-1]
        j -= 1
        
    # We built the strings backwards, so reverse them before returning
    return align1[::-1], align2[::-1]

# --- Let's test it out! ---
sequence_A = "GCATGCG"
sequence_B = "GATTACA"

aligned_A, aligned_B = needleman_wunsch(sequence_A, sequence_B)

print("Sequence 1: ", aligned_A)
print("Sequence 2: ", aligned_B)

# Optional: Print visual match lines
match_line = "".join(["|" if a == b else " " for a, b in zip(aligned_A, aligned_B)])
print("\nVisual Alignment:")
print(aligned_A)
print(match_line)
print(aligned_B)