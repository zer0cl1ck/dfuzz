# dfuzz
dfuzz is a Python-based, multithreaded directory fuzzing tool that scans multiple URLs (from a file) using a single wordlist, similar to dirsearch. It supports recursive scanning, customizable status code filtering, and an optional deduplication feature to skip repeated content lengths, helping reduce noise in results.

Steps to Set Up & Run the Script

# 1. Install Python
Make sure Python 3 is installed:
python3 --version

# 2. Create a Working Directory
mkdir dfuzz && cd dfuzz

# 3. Save the Script
Save the code provided as dfuzz.py.
nano dfuzz.py | Using "git clone"
Paste the code and save

# 4. Install Dependencies
pip install requests colorama tqdm

# 5. Prepare Input Files
URLs file (urls.txt): One base URL per line
Example:
https://example.com
https://test.com

Wordlist file (wordlist.txt): Paths to fuzz

# 6. Run the Script
python3 dfuzz.py -f urls.txt -w wordlist.txt -i 200,301,302 -r 1 -t 20 --auto-duplicate -o results.txt


## Options:

-f → file containing base URLs

-w → wordlist file

-i → status codes to match (default: 200,301,302)

-r → recursive depth (default: 0)

-t → number of threads (default: 10, max: 100)

--auto-duplicate → skip repeated content lengths (>3 times)

-o → save results to a file
