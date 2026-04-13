#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    print("No files provided")
    sys.exit(0)

for filepath in sys.argv[1:]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        sorted_lines = sorted(line for line in lines if line.strip())

        with open(filepath, 'w', encoding='utf-8') as f:
            for line in sorted_lines:
                f.write(line if line.endswith('\n') else line + '\n')

        print(f"Sorted: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
