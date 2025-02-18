#!/usr/bin/python3
import argparse
import asyncio
import re
import os
import sys
from urllib.parse import urljoin, urlparse
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from colorama import Fore, init
import jsbeautifier
import warnings

# Code by M3Y
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
init(autoreset=True)

def show_banner(domain):
	banner = f"""
	{Fore.RED}███████╗███████╗███████╗██╗███╗   ██╗██████╗ ███████╗██████╗ 
	{Fore.YELLOW}╚══███╔╝╚══███╔╝██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
	{Fore.GREEN}  ███╔╝   ███╔╝ █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
	{Fore.CYAN} ███╔╝   ███╔╝  ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
	{Fore.MAGENTA}███████╗███████╗███████╗██║██║ ╚████║██████╔╝███████╗██║  ██║
	{Fore.WHITE}╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
	{Fore.BLUE}──────────────────────────────────────────────────────────────
	{Fore.WHITE} Target: {Fore.CYAN}{domain}
	{Fore.BLUE}──────────────────────────────────────────────────────────────
	{Fore.WHITE} Version: {Fore.YELLOW}1.0 | {Fore.WHITE}Author: {Fore.GREEN}@M3Y
	{Fore.BLUE}──────────────────────────────────────────────────────────────
	"""
	print(banner)

class JSFinder:
    def __init__(self, domain, output_file, concurrency=20, wordlist=None, enable_brute=False):
        self.base_urls = [f"http://{domain}", f"https://{domain}"]
        self.domain = domain
        self.output_file = output_file
        self.concurrency = concurrency
        self.visited_urls = set()
        self.found_js = set()
        self.wordlist = wordlist or []
        self.enable_brute = enable_brute
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.js_pattern = re.compile(r'\.js$|\.mjs$|\.jsx$', re.IGNORECASE)
        self.output_dir = Path(domain.replace('/', '_'))
        self.setup_directories()

    def setup_directories(self):
        self.output_dir.mkdir(exist_ok=True)

    def sanitize_filename(self, url):
        clean = re.sub(r'^https?://', '', url)
        clean = re.sub(r'[^a-zA-Z0-9\-_\.]', '_', clean)
        return clean[:150] + '.js'

    async def download_and_save(self, session, url):
        try:
            async with session.get(url, timeout=20, ssl=False) as response:
                if response.status == 200:
                    content = await response.text()
                    filename = self.sanitize_filename(url)
                    self.beautify_js(content, filename)
                    with open(self.output_file, 'a') as f:
                        f.write(f"{url}\n")
        except Exception as e:
            print(f"{Fore.RED}[-] Error downloading: {url} - {str(e)}")

    def beautify_js(self, content, filename):
        try:
            opts = jsbeautifier.default_options()
            opts.indent_size = 2
            opts.space_in_empty_paren = True
            beautified = jsbeautifier.beautify(content, opts)
            
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(beautified)
        except Exception as e:
            print(f"{Fore.RED}[-] Error formatting {filename}: {str(e)}")

    async def validate_js(self, session, url):
        try:
            async with session.head(url, allow_redirects=True, timeout=15, ssl=False) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if any(t in content_type for t in ['javascript', 'ecmascript']) or self.js_pattern.search(url):
                        return url, True
                return url, False
        except Exception as e:
            return url, False

    async def fetch(self, session, url):
        try:
            async with session.get(url, headers=self.headers, timeout=15, ssl=False) as response:
                if response.status in [200, 301, 302]:
                    content = await response.text()
                    return content, str(response.url)
                return None, None
        except Exception as e:
            return None, None

    def extract_links(self, html, base_url):
        try:
            if re.search(r'<\?xml|<!DOCTYPE|rss|feed', html, re.IGNORECASE):
                soup = BeautifulSoup(html, 'xml')
            else:
                soup = BeautifulSoup(html, 'lxml')
        except:
            soup = BeautifulSoup(html, 'html.parser')

        links = set()
        tags = {'script': 'src', 'a': 'href', 'link': 'href', 'img': 'src', 'iframe': 'src'}
        
        for tag, attr in tags.items():
            for element in soup.find_all(tag, {attr: True}):
                links.add(element[attr])
        
        found_js = re.findall(r'["\'](.*?\.js[^"\']*)["\']', html, re.IGNORECASE)
        links.update(found_js)
        
        clean_links = set()
        for link in links:
            try:
                full_url = urljoin(base_url, link).split('#')[0].split('?')[0]
                parsed = urlparse(full_url)
                if parsed.netloc.endswith(self.domain):
                    clean_links.add(full_url)
            except:
                continue
                
        return clean_links

    async def process_page(self, session, url):
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        
        content, final_url = await self.fetch(session, url)
        if not content:
            return

        all_links = self.extract_links(content, final_url)
        
        js_links = [link for link in all_links if self.js_pattern.search(link)]
        for js_link in js_links:
            validated_url, is_valid = await self.validate_js(session, js_link)
            if is_valid and validated_url not in self.found_js:
                self.found_js.add(validated_url)
                await self.download_and_save(session, validated_url)
        
        for link in all_links:
            if link not in self.visited_urls:
                asyncio.create_task(self.process_page(session, link))

    async def brute_force(self, session):
        paths = {
            path 
            for word in self.wordlist 
            for path in (
                f"/{word}", 
                f"/{word}.js", 
                f"/{word}/main.js"
            )
        }
        
        tasks = []
        for path in paths:
            for base_url in self.base_urls:
                url = f"{base_url}{path}"
                tasks.append(self.validate_js(session, url))
        
        for i in range(0, len(tasks), self.concurrency):
            batch = tasks[i:i+self.concurrency]
            results = await asyncio.gather(*batch)
            for url, is_valid in results:
                if is_valid and url not in self.found_js:
                    self.found_js.add(url)
                    await self.download_and_save(session, url)

    async def start(self):
        connector = aiohttp.TCPConnector(limit=self.concurrency, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.process_page(session, base_url) for base_url in self.base_urls]
            
            if self.enable_brute and self.wordlist:
                tasks.append(self.brute_force(session))
            
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Javascript File Search')
    parser.add_argument('-d', '--domain', required=True, help='Target domain (example: example.com)')
    parser.add_argument('-o', '--output', required=True, help='file to save urls')
    parser.add_argument('-c', '--concurrency', type=int, default=20, help='Concurrent Connections')
    parser.add_argument('-w', '--wordlist', help='Wordlist for brute force')
    parser.add_argument('--brute', action='store_true', help='Enable brute force')
    
    args = parser.parse_args()
    show_banner(args.domain)

    wordlist = Path(args.wordlist).read_text().splitlines() if args.wordlist else []

    finder = JSFinder(
        domain=args.domain,
        output_file=args.output,
        concurrency=args.concurrency,
        wordlist=wordlist,
        enable_brute=args.brute
    )

    if args.domain.startswith("https://"):
       print("[-] Just domain, example: www.example.com")
       sys.exit(0)

    print(f"{Fore.CYAN}[*] Starting scan in: {args.domain}")
    try:
        asyncio.run(finder.start())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Interrupted Scan")
    finally:
        print(f"\n{Fore.CYAN}[*] Final Summary:")
        print(f"{Fore.CYAN}[*] JS files found: {len(finder.found_js)}")
        print(f"{Fore.CYAN}[*] File directory: {finder.output_dir}")
        print(f"{Fore.CYAN}[*] List of URLS stored in: {args.output}")
