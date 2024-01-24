from datetime import datetime

# Read the text file
with open('your_file.txt', 'r') as file:
    lines = file.readlines()

date_formats = {}  # To store date formats and their counts
legacy_count = 0

# Define a list of potential date format patterns
date_format_patterns = [
    '%Y-%m-%d %H:%M:%S',
    '%d/%m/%Y %H:%M:%S',
    '%Y-%m-%d',
    '%d/%m/%Y',
]

for line in lines:
    line = line.strip()  # Remove leading/trailing whitespace
    found_format = False
    for date_format_pattern in date_format_patterns:
        try:
            datetime.strptime(line, date_format_pattern)
            date_formats[date_format_pattern] = date_formats.get(date_format_pattern, 0) + 1
            found_format = True
            break  # If successful, no need to check other patterns
        except ValueError:
            pass  # Continue checking other patterns

    if not found_format and line.lower() == 'legacy':
        legacy_count += 1

# Print unique date formats and their counts
for date_format, count in date_formats.items():
    print(f"Date format: {date_format}, Count: {count}")

print(f"Total unique date formats: {len(date_formats)}")
print(f"Legacy count: {legacy_count}")
