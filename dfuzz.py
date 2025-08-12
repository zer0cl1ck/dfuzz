#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urljoin
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
from tqdm import tqdm
import threading

init(autoreset=True)

print_lock = threading.Lock()
length_lock = threading.Lock()
content_length_counter = {}

def color_status(status):
    if status == 200:
        return Fore.GREEN + str(status) + Style.RESET_ALL
    elif status in (301, 302):
        return Fore.YELLOW + str(status) + Style.RESET_ALL
    elif status in (401, 403):
        return Fore.MAGENTA + str(status) + Style.RESET_ALL
    else:
        return Fore.RED + str(status) + Style.RESET_ALL

def color_length(length):
    return Fore.YELLOW + f"length: {length}" + Style.RESET_ALL

def scan_path(base_url, path, valid_codes, depth, wordlist, current_depth=1, auto_duplicate=False):
    target = urljoin(base_url.rstrip('/') + '/', path)
    found = []

    try:
        response = requests.get(target, timeout=5, allow_redirects=True)
        if response.status_code in valid_codes:
            length = len(response.content)

            if auto_duplicate:
                with length_lock:
                    content_length_counter[length] = content_length_counter.get(length, 0) + 1
                    if content_length_counter[length] > 3:
                        return []  # Skip duplicate-like content

            with print_lock:
                print(f"[{color_status(response.status_code)}] {target} [{color_length(length)}]")

            found.append(target)

            if depth and current_depth < depth and target.endswith('/'):
                try:
                    with open(wordlist, 'r') as wlist:
                        sub_paths = [line.strip() for line in wlist if line.strip()]
                    for sub_path in sub_paths:
                        found += scan_path(target, sub_path, valid_codes, depth, wordlist, current_depth + 1, auto_duplicate)
                except FileNotFoundError:
                    pass
    except requests.RequestException:
        pass

    return found

def scan_url(base_url, wordlist, valid_codes, depth, threads, auto_duplicate=False):
    try:
        with open(wordlist, 'r') as wlist:
            paths = [line.strip() for line in wlist if line.strip()]
    except FileNotFoundError:
        with print_lock:
            print(f"[!] Wordlist not found: {wordlist}")
        return []

    found_urls = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_path, base_url, path, valid_codes, depth, wordlist, 1, auto_duplicate): path for path in paths}
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Bruteforcing {base_url}"):
            result = future.result()
            if result:
                found_urls.extend(result)

    return found_urls

def main():
    parser = argparse.ArgumentParser(description="Threaded Dirsearch-style Fuzzer with Optional Deduplication")
    parser.add_argument('-f', required=True, help='File containing base URLs (one per line)')
    parser.add_argument('-w', required=True, help='Wordlist file')
    parser.add_argument('-i', help='Comma-separated status codes (default: 200,301,302)', default='200,301,302')
    parser.add_argument('-r', type=int, help='Recursive depth (default: 0)', default=0)
    parser.add_argument('-o', help='Output file for results', default=None)
    parser.add_argument('-t', type=int, help='Number of threads (1–100, default: 10)', default=10)
    parser.add_argument('--auto-duplicate', action='store_true', help='Filter out responses with repeated content lengths (>3)')

    args = parser.parse_args()
    threads = max(1, min(args.t, 100))

    try:
        with open(args.f, 'r') as url_file:
            urls = [line.strip() for line in url_file if line.strip()]
    except FileNotFoundError:
        print(f"[!] URL input file not found: {args.f}")
        return

    try:
        valid_codes = set(int(code.strip()) for code in args.i.split(','))
    except ValueError:
        print(f"[!] Invalid status code format in: {args.i}")
        return

    all_found_urls = []
    total = len(urls)

    for idx, url in enumerate(urls, start=1):
        print(f"\n[+] Scanning ({idx}/{total}) [{round((idx/total)*100)}%]: {url}")
        found = scan_url(url, args.w, valid_codes, args.r, threads, args.auto_duplicate)
        all_found_urls.extend(found)

    if args.o:
        try:
            with open(args.o, 'w') as out:
                for u in all_found_urls:
                    out.write(u + '\n')
            print(f"\n[+] Output saved to {args.o}")
        except IOError:
            print(f"[!] Could not write to output file: {args.o}")

if __name__ == "__main__":
    main()
