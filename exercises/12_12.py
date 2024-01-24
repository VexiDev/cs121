import sys

def read_numbers_and_compute_average(file_path):
    with open(file_path, 'r+') as file:
        numbers = file.readlines()

        # Compute the sum and count of the numbers
        total_sum = 0
        count = 0
        for num in numbers:
            try:
                total_sum += float(num.strip())
                count += 1
            except ValueError:
                pass  # Ignore lines that are not numbers

        # Calculate average
        if count > 0:
            average = total_sum / count
        else:
            average = 0

        # Append the result to the file
        file.write(f"\nAverage: {average}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 12_12.py <filename>")
        sys.exit(1)

    file_path = f"/Users/vexi/Documents/{sys.argv[1]}"
    read_numbers_and_compute_average(file_path)
