"""
UHC Insurance Policy Web Scraper

This script scrapes insurance policies from UHC's website and prepares them
for ingestion into ChromaDB vector database.

Data Source: https://www.uhcprovider.com/en/policies-protocols/commercial-policies/commercial-medical-drug-policies.html
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import json
from pathlib import Path
import re
from datetime import datetime

class UHCScraper:
    """Scraper for UHC commercial medical drug policies"""

    BASE_URL = "https://www.uhcprovider.com"
    POLICIES_URL = f"{BASE_URL}/en/policies-protocols/commercial-policies/commercial-medical-drug-policies.html"

    def __init__(self, output_dir: str = "data/raw"):
        """
        Initialize scraper

        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_policy_links(self) -> List[Dict[str, str]]:
        """
        Get all policy links from the main policies page

        Returns:
            List of dictionaries with policy metadata
        """
        print(f"Fetching policy links from: {self.POLICIES_URL}")

        try:
            response = self.session.get(self.POLICIES_URL, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching policies page: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all policy links
        # Note: This is a simplified version - actual scraping logic depends on UHC's HTML structure
        policy_links = []

        # Look for policy links in the page
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Filter for policy links
            if 'medical-drug-policy' in href.lower() or 'coverage-determination' in href.lower():
                full_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"

                policy_links.append({
                    'title': text,
                    'url': full_url,
                    'policy_id': self._extract_policy_id(href)
                })

        print(f"Found {len(policy_links)} policy links")
        return policy_links

    def _extract_policy_id(self, href: str) -> str:
        """Extract policy ID from URL"""
        # Try to extract ID from URL pattern
        match = re.search(r'([A-Z0-9\-]+)\.html', href)
        if match:
            return match.group(1)

        # Fallback: use last part of path
        return href.split('/')[-1].replace('.html', '')

    def scrape_policy(self, policy_url: str) -> Optional[Dict]:
        """
        Scrape content from a single policy page

        Args:
            policy_url: URL of the policy page

        Returns:
            Dictionary with policy content and metadata
        """
        print(f"Scraping: {policy_url}")

        try:
            response = self.session.get(policy_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error scraping {policy_url}: {e}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract content
        # Note: Adjust selectors based on actual UHC page structure
        title = soup.find('h1')
        title_text = title.get_text(strip=True) if title else "Unknown Policy"

        # Get main content
        content_div = soup.find('div', class_='content') or soup.find('article') or soup.find('main')

        if not content_div:
            # Fallback: get all paragraphs
            content_text = '\n\n'.join([p.get_text(strip=True) for p in soup.find_all('p')])
        else:
            content_text = content_div.get_text(separator='\n', strip=True)

        # Extract sections
        sections = self._extract_sections(soup)

        return {
            'title': title_text,
            'url': policy_url,
            'content': content_text,
            'sections': sections,
            'scraped_at': datetime.now().isoformat()
        }

    def _extract_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specific sections from policy page"""
        sections = {}

        # Common section headers in insurance policies
        section_headers = [
            'coverage criteria',
            'coverage determination',
            'limitations',
            'exclusions',
            'definitions',
            'background',
            'benefit considerations',
            'coding information',
            'cpt codes',
            'icd codes',
            'references'
        ]

        for header in section_headers:
            # Find header (h2, h3, or strong tag)
            header_elem = soup.find(['h2', 'h3', 'h4', 'strong'],
                                   string=re.compile(header, re.IGNORECASE))

            if header_elem:
                # Get content after header
                content = []
                for sibling in header_elem.find_next_siblings():
                    if sibling.name in ['h2', 'h3', 'h4']:
                        break  # Stop at next header
                    content.append(sibling.get_text(strip=True))

                sections[header] = '\n'.join(content)

        return sections

    def scrape_all_policies(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape all UHC policies

        Args:
            limit: Optional limit on number of policies to scrape (for testing)

        Returns:
            List of policy dictionaries
        """
        policy_links = self.get_policy_links()

        if limit:
            policy_links = policy_links[:limit]
            print(f"Limiting to {limit} policies for testing")

        policies = []

        for i, link in enumerate(policy_links, 1):
            print(f"[{i}/{len(policy_links)}] Scraping: {link['title']}")

            policy_data = self.scrape_policy(link['url'])

            if policy_data:
                policy_data['policy_id'] = link['policy_id']
                policies.append(policy_data)

                # Save individual policy
                self._save_policy(policy_data)

            # Be respectful - add delay between requests
            time.sleep(2)

        return policies

    def _save_policy(self, policy_data: Dict):
        """Save individual policy to JSON file"""
        filename = f"{policy_data['policy_id']}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(policy_data, f, indent=2, ensure_ascii=False)

        print(f"  Saved to: {filepath}")

    def save_all_policies(self, policies: List[Dict], filename: str = "uhc_policies.json"):
        """Save all policies to a single JSON file"""
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(policies, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(policies)} policies to: {filepath}")

def main():
    """Main scraping workflow"""
    print("="*80)
    print("UHC POLICY SCRAPER")
    print("="*80)

    scraper = UHCScraper(output_dir="data/raw")

    # For testing, limit to 5 policies
    # For production, set limit=None to scrape all
    policies = scraper.scrape_all_policies(limit=5)

    # Save combined file
    scraper.save_all_policies(policies)

    print("\n" + "="*80)
    print(f"✅ SCRAPING COMPLETE - {len(policies)} policies scraped")
    print("="*80)

if __name__ == "__main__":
    main()
