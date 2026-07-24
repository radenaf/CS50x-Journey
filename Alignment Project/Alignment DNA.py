def needleman_wunsch(seq1, seq2, match_reward=1, mismatch_penalty=-1, gap_penalty=-1):
    # 1. Matrix Grid Setup
    rows, cols = len(seq1) + 1, len(seq2) + 1
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows): matrix[i][0] = i * gap_penalty
    for j in range(cols): matrix[0][j] = j * gap_penalty
        
    # 2. Fill in the Matrix 
    for i in range(1, rows):
        for j in range(1, cols):
            is_match = seq1[i-1] == seq2[j-1]
            diagonal_score = matrix[i-1][j-1] + (match_reward if is_match else mismatch_penalty)
            up_score = matrix[i-1][j] + gap_penalty
            left_score = matrix[i][j-1] + gap_penalty
            
            matrix[i][j] = max(diagonal_score, up_score, left_score)
            
    # Capture the final alignment score before tracing back
    final_score = matrix[rows-1][cols-1]
            
    # 3. Traceback 
    align1, align2 = "", ""
    i, j = len(seq1), len(seq2)
    
    while i > 0 and j > 0:
        current_score = matrix[i][j]
        diagonal_score = matrix[i-1][j-1]
        up_score = matrix[i-1][j]
        
        is_match = seq1[i-1] == seq2[j-1]
        
        if current_score == diagonal_score + (match_reward if is_match else mismatch_penalty):
            align1 += seq1[i-1]
            align2 += seq2[j-1]
            i -= 1
            j -= 1
        elif current_score == up_score + gap_penalty:
            align1 += seq1[i-1]
            align2 += "-"
            i -= 1
        else:
            align1 += "-"
            align2 += seq2[j-1]
            j -= 1
            
    while i > 0:
        align1 += seq1[i-1]
        align2 += "-"
        i -= 1
    while j > 0:
        align1 += "-"
        align2 += seq2[j-1]
        j -= 1
        
    return align1[::-1], align2[::-1], final_score

# --- Interactive Terminal Interface ---
print("--- DNA Sequence Aligner ---")
sequence_A = input("Enter the first sequence: ").replace(" ", "").upper()
sequence_B = input("Enter the second sequence: ").replace(" ", "").upper()

# Run the alignment
aligned_A, aligned_B, score = needleman_wunsch(sequence_A, sequence_B)

# Calculate stats
align_len = len(aligned_A)
identities = sum(1 for a, b in zip(aligned_A, aligned_B) if a == b)
gaps = sum(1 for a, b in zip(aligned_A, aligned_B) if a == '-' or b == '-')

# Prevent division by zero if inputs are empty
if align_len > 0:
    id_pct = (identities / align_len) * 100
    gap_pct = (gaps / align_len) * 100
else:
    id_pct, gap_pct = 0.0, 0.0

# Print the visual alignment first
print("\nVisual Alignment:")
print(aligned_A)
print("".join(["|" if a == b else " " for a, b in zip(aligned_A, aligned_B)]))
print(aligned_B)

# Print the metadata summary report matching the image format
print("\nAlignment type: DNA alignment")
print("\nMatrix: SIMPLE_SCORING")
print("Gap penalty: -1.0")
print(f"Score: {float(score):.1f}")
print(f"Sequence 1 length: {len(sequence_A)}")
print(f"Sequence 2 length: {len(sequence_B)}")
print(f"Alignment length:  {align_len}")
print(f"Identity:         {identities}/{align_len} ({id_pct:.2f}%)")
print(f"Gaps:             {gaps}/{align_len} ({gap_pct:.2f}%)")