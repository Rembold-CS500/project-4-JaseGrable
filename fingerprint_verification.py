def read_print(filename):
    """Reads the given print and returns a dictionary with all info."""
    with open(filename, 'r') as file: 
        data = {}
        data['name'] = file.readline().strip()
        data['width'] = int(file.readline().strip())
        data['height'] = int(file.readline().strip())

        fingerprint = []
        for line in file:
            # Preserve the line as it is, including spaces
            fingerprint.append(list(line.rstrip('\n')))  # Only strip newline characters, not spaces

        data['fingerprint'] = fingerprint
        return data

def simple_check(fingerprint1, fingerprint2):
    """Compares the fingerprint portions of two dictionaries. Returns true if the data is a match"""
    return fingerprint1['fingerprint'] == fingerprint2['fingerprint']

def variant_check(fingerprint1, fingerprint2, threshold=95.0):
    """Compares two fingerprints and returns True if percentage of matching pixels is above the threshold"""
    fp1 = fingerprint1['fingerprint']
    fp2 = fingerprint2['fingerprint']

    # Debug: Print dimensions of both fingerprints
    print(f"Fingerprint 1 dimensions: {len(fp1)}x{len(fp1[0])}")
    print(f"Fingerprint 2 dimensions: {len(fp2)}x{len(fp2[0])}")

    if len(fp1) != len(fp2) or any(len(row1) != len(row2) for row1, row2 in zip(fp1, fp2)):
        raise ValueError("Fingerprints must have the same dimensions.")

    total_pixels = 0 
    matching_pixels = 0 

    for row1, row2 in zip(fp1, fp2):
        for char1, char2 in zip(row1, row2):
            total_pixels += 1
            if char1 == char2: 
                matching_pixels += 1 

    matching_percentage = (matching_pixels / total_pixels) * 100 

    print(f"Matching percentage: {matching_percentage:.2f}%")

    return matching_percentage >= threshold

def shifted_check(fingerprint1, fingerprint2, threshold=95.0, max_shift=5, return_percentage=False):
    '''Compares two fingerprints allowing for shifts and returns True if the best match percentage
    is above the threshold.'''
    fp1 = fingerprint1['fingerprint']
    fp2 = fingerprint2['fingerprint']
    height = len(fp1)
    width = len(fp1[0])

    max_match_percentage = 0.0 

    # Iterate over possible shifts
    for shift_y in range(-max_shift, max_shift + 1):
        for shift_x in range(-max_shift, max_shift + 1):
            matching_pixels = 0
            total_pixels = 0 

            # Determine overlapping region considering the shift
            y_start_fp1 = max(0, -shift_y)
            y_start_fp2 = max(0, shift_y)
            y_end = min(height, height - abs(shift_y))

            x_start_fp1 = max(0, -shift_x)
            x_start_fp2 = max(0, shift_x)
            x_end = min(width, width - abs(shift_x))

            # Compare the fingerprints within the overlapping region
            for y in range(y_end):
                for x in range(x_end):
                    fp1_y = y + y_start_fp1
                    fp1_x = x + x_start_fp1
                    fp2_y = y + y_start_fp2
                    fp2_x = x + x_start_fp2

                    if fp1[fp1_y][fp1_x] == fp2[fp2_y][fp2_x]:
                        matching_pixels += 1
                    total_pixels += 1

            # Calculate match percentage for the shift
            if total_pixels > 0: 
                matching_percentage = (matching_pixels / total_pixels) * 100 
                if matching_percentage > max_match_percentage:
                    max_match_percentage = matching_percentage

    print(f"Maximum matching percentage with shifts: {max_match_percentage:.2f}%")
    
    if return_percentage:
        return max_match_percentage

    return max_match_percentage >= threshold

def find_best_match(partial_fingerprints, full_fingerprints, threshold=95.0):
    """Finds the best match for each partial fingerprint from the full fingerprints."""
    results = {}

    for partial in partial_fingerprints:
        best_match = None
        best_percentage = 0

        print(f"Matching for partial fingerprint: {partial['name']}")

        for full in full_fingerprints:
            match_percentage = shifted_check(partial, full, return_percentage=True)

            print(f"Comparing with full fingerprint: {full['name']} - Match percentage: {match_percentage:.2f}%")

            if match_percentage > best_percentage:
                best_percentage = match_percentage
                best_match = full

        if best_match and best_percentage >= threshold:
            results[partial['name']] = (best_match['name'], best_percentage)
        else:
            results[partial['name']] = (None, 0.00)

    return results

if __name__ == '__main__':
    # Load fingerprints
    original = read_print("./prints/User1_Original.txt")
    variant1 = read_print("./prints/User1_Variant1.txt")
    shifted_variant1 = read_print("./prints/User1_ShiftedVariant1.txt")
    variant2 = read_print("./prints/User1_Variant2.txt")
    partial_fingerprints = [
        read_print("./prints/partials/Partial1.txt"),
        read_print("./prints/partials/Partial2.txt"),
        # Add more partial fingerprints as needed
    ]
    full_fingerprints = [original, variant1, shifted_variant1, variant2]

    # Find best matches
    matches = find_best_match(partial_fingerprints, full_fingerprints)
    for partial_name, (best_match_name, percentage) in matches.items():
        print(f"Best match for {partial_name}: {best_match_name} with {percentage:.2f}% matching")

