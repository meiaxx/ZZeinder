# 🕵️ ZZeinder - JavaScript File Hunter

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

ZZeinder is a powerful tool for discovering and downloading JavaScript files from websites. It combines web crawling and brute-forcing techniques to find hidden JS files, making it ideal for security researchers and web developers.

---

## Features ✨
- **Web Crawling**: Automatically discovers JS files by crawling the target website.
- **Brute-Force Mode**: Finds JS files using a wordlist.
- **File Beautification**: Downloads and formats JS files for easy reading.
- **Concurrency Support**: Fast scanning with configurable concurrent connections.
- **Error Handling**: Robust validation and error recovery.

---

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ZZeinder.git
   cd ZZeinder  
   pip install -r requirements.txt
   ```

## Usage 🚀
   Basic Scan
      
   python3 zzeinder.py -d example.com -o results.txt
   
   Brute-Force Mode
   
   python3 zZeinder.py -d example.com -o results.txt --brute -w wordlist.txt
   
   Advanced Options
   
   python3 zzeinder.py -d example.com -o results.txt -c 50 --brute -w wordlist.txt

## Options 📋
   Argument	Description	Default
   -d, --domain	Target domain (e.g., example.com)	Required
   -o, --output	Output file for results	Required
   -c, --concurrency	Concurrent connections (1-500)	20
   -w, --wordlist	Wordlist for brute-force	None
   --brute	Enable brute-force mode	False

## Examples 🧪
   Example 1: Basic Scan
   bash
   Copy
   
   python3 zzeinder.py -d example.com -o js_files.txt
   
   Example 2: Brute-Force with Custom Wordlist
   bash
   Copy
   
   python3 zzeinder.py -d example.com -o js_files.txt --brute -w custom_wordlist.txt
   
## Contributing 🤝
   
   Contributions are welcome! Please follow these steps:
   
      1. Fork the repository.
   
      2. Create a new branch (git checkout -b feature/YourFeature).
   
      3. Commit your changes (git commit -m 'Add some feature').
   
      4. Push to the branch (git push origin feature/YourFeature).
   
      5. Open a pull request.
   
