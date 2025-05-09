
import os
import json
from collections import defaultdict

def load_vc_input():
    with open("data/vc_input.json", "r") as f:
        return json.load(f)

def get_scraped_vcs():
    return set(f.replace(".jsonl", "") for f in os.listdir("data/raw/vcs"))

def get_scraped_portfolios():
    return set(f.replace(".jsonl", "") for f in os.listdir("data/raw/portfolio"))

def load_failed_scrapes():
    failed = set()
    if os.path.exists("data/failed_scrapes.txt"):
        with open("data/failed_scrapes.txt", "r") as f:
            failed = set(line.strip() for line in f if line.strip())
    return failed

def extract_domain(url):
    try:
        return url.split("//")[-1].split("/")[0]
    except:
        return url

def main():
    vcs = load_vc_input()
    scraped_vcs = get_scraped_vcs()
    scraped_portfolios = get_scraped_portfolios()
    failed_urls = load_failed_scrapes()

    report_lines = []
    report_lines.append("🧠 VC Scraping Summary Report")
    report_lines.append("="*40 + "\n")

    total_vcs = len(vcs)
    scraped_vc_count = sum(1 for vc in vcs if vc["name"] in scraped_vcs)
    total_portfolios = sum(len(vc.get("portfolio_urls", [])) for vc in vcs)
    scraped_portfolio_count = len(scraped_portfolios)
    failed_count = len(failed_urls)

    report_lines.append(f"Total VCs in input: {total_vcs}")
    report_lines.append(f"VCs successfully scraped: {scraped_vc_count}")
    report_lines.append(f"Total portfolio companies listed: {total_portfolios}")
    report_lines.append(f"Portfolio scrapes succeeded: {scraped_portfolio_count}")
    report_lines.append(f"Failed scrapes: {failed_count}")
    report_lines.append(f"Overall scrape success rate: {round((scraped_vc_count + scraped_portfolio_count) / (total_vcs + total_portfolios) * 100, 2)}%")
    report_lines.append("\n")

    report_lines.append("📋 VC-by-VC Breakdown")
    report_lines.append("-"*40)
    header = f"{'VC Name':<20} {'VC Scraped':<12} {'#Portfolios':<12} {'Portfolios Scraped':<20} {'Success %':<10} {'Failures':<10}"
    report_lines.append(header)
    report_lines.append("-"*len(header))

    failed_map = defaultdict(list)
    for url in failed_urls:
        domain = extract_domain(url)
        for vc in vcs:
            if url == vc.get("url") or url in vc.get("portfolio_urls", []):
                failed_map[vc["name"]].append(url)

    for vc in vcs:
        vc_name = vc["name"]
        vc_url = vc["url"]
        portfolios = vc.get("portfolio_urls", [])
        num_portfolios = len(portfolios)
        scraped_vc = "✅" if vc_name in scraped_vcs else "❌"
        scraped_portfolios_count = sum(1 for p in portfolios if extract_domain(p) in scraped_portfolios)
        success_rate = round(scraped_portfolios_count / max(1, num_portfolios) * 100, 1)
        failed_for_vc = failed_map.get(vc_name, [])
        report_lines.append(f"{vc_name:<20} {scraped_vc:<12} {num_portfolios:<12} {scraped_portfolios_count:<20} {success_rate:<10}% {len(failed_for_vc):<10}")

    report_lines.append("\n📛 Failed URLs by VC")
    report_lines.append("-"*30)
    for vc_name, urls in failed_map.items():
        report_lines.append(f"❌ {vc_name}:")
        for u in urls:
            report_lines.append(f"    - {u}")

    report_lines.append("\n✅ End of Report")

    with open("scrape_report.txt", "w") as f:
        f.write("\n".join(report_lines))

    print("✅ Report written to scrape_report.txt")

if __name__ == "__main__":
    main()
