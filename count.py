import json

with open('search_results.json', 'r') as f:
    data = json.load(f)
    count = 0
    for item in data:
        count += 1
    print(count)