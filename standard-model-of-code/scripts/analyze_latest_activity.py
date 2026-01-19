import csv
import sys

def main():
    csv_file = "/Users/lech/PROJECTS_all/PROJECT_elements/project_elements_file_timestamps.csv"
    
    entries = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Sort by modified_epoch descending
    entries.sort(key=lambda x: int(x['modified_epoch']), reverse=True)
    
    print(f"Total files: {len(entries)}")
    print("--- Top 10 Most Recently Modified Files ---")
    for i, entry in enumerate(entries[:10]):
        print(f"{i+1}. {entry['modified_iso']} - {entry['path']}")

if __name__ == "__main__":
    main()
