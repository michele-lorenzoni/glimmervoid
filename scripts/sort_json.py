#!/usr/bin/env python3
import json
import sys

if len(sys.argv) < 2:
    print("No files provided")
    sys.exit(0)

for filepath in sys.argv[1:]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')
        
        print(f"Sorted: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        sys.exit(1)