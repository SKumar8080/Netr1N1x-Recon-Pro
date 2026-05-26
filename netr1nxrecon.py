#!/usr/bin/env python3
"""
███████╗██╗   ██╗██╗     ██╗     ██╗   ██╗███╗   ███╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔════╝██║   ██║██║     ██║     ██║   ██║████╗ ████║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
█████╗  ██║   ██║██║     ██║     ██║   ██║██╔████╔██║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══╝  ██║   ██║██║     ██║     ██║   ██║██║╚██╔╝██║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║     ╚██████╔╝███████╗███████╗╚██████╔╝██║ ╚═╝ ██║     ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                           by Srimant Kumar
                                                                                        https://netrinix.com
"""

import os, sys, subprocess, json, time, shutil, re, logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import argparse
import tempfile
import signal

# ---------------------------- Configuration ----------------------------
TOOLS_DIR = os.path.join(os.getcwd(), "netrinix_tools")
WORDLIST_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt"
WORDLIST_PATH = os.path.join(TOOLS_DIR, "common.txt")
GO_BIN = os.path.expanduser("~/go/bin")

# Virtual environment for Python-based tools
VENV_DIR = os.path.join(TOOLS_DIR, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python3")
VENV_PIP = os.path.join(VENV_DIR, "bin", "pip")

# Tools definition: check_cmd, install_cmd, type
TOOLS = {
    "nmap": {
        "check": "which nmap",
        "install": "sudo apt-get install -y nmap",
        "type": "binary"
    },
    "subfinder": {
        "check": "which subfinder",
        "install": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "type": "go"
    },
    "gobuster": {
        "check": "which gobuster",
        "install": "go install github.com/OJ/gobuster/v3@latest",
        "type": "go"
    },
    "subjs": {
        "check": "which subjs",
        "install": "go install github.com/lc/subjs@latest",
        "type": "go"
    },
    "httpx": {
        "check": "which httpx",
        "install": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
        "type": "go"
    },
    "nuclei": {
        "check": "which nuclei",
        "install": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        "type": "go"
    },
    "waybackurls": {
        "check": "which waybackurls",
        "install": "go install github.com/tomnomnom/waybackurls@latest",
        "type": "go"
    },
    "linkfinder": {
        "check": os.path.join(TOOLS_DIR, "LinkFinder", "linkfinder.py"),
        "install": f"git clone https://github.com/GerbenJavado/LinkFinder.git {TOOLS_DIR}/LinkFinder && cd {TOOLS_DIR}/LinkFinder && {{venv_pip}} install -r requirements.txt",
        "type": "python_script"
    },
    "secretfinder": {
        "check": os.path.join(TOOLS_DIR, "SecretFinder", "SecretFinder.py"),
        "install": f"git clone https://github.com/m4ll0k/SecretFinder.git {TOOLS_DIR}/SecretFinder && cd {TOOLS_DIR}/SecretFinder && {{venv_pip}} install -r requirements.txt",
        "type": "python_script"
    }
}

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# ---------------------------- Banner ----------------------------
BANNER = f"""
{RED}███╗   ██╗███████╗████████╗██████╗ ██╗███╗   ██╗██╗██╗  ██╗{RESET}
{RED}████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║████╗  ██║██║╚██╗██╔╝{RESET}
{RED}██╔██╗ ██║█████╗     ██║   ██████╔╝██║██╔██╗ ██║██║ ╚███╔╝ {RESET}
{RED}██║╚██╗██║██╔══╝     ██║   ██╔══██╗██║██║╚██╗██║██║ ██╔██╗ {RESET}
{RED}██║ ╚████║███████╗   ██║   ██║  ██║██║██║ ╚████║██║██╔╝ ██╗{RESET}
{RED}╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝{RESET}
{YELLOW}██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗{RESET}
{YELLOW}██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║{RESET}
{YELLOW}██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║{RESET}
{YELLOW}██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║{RESET}
{YELLOW}██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║{RESET}
{YELLOW}╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝{RESET}
{CYAN}       Srimant Kumar - https://netrinix.com{RESET}
"""

# ---------------------------- Logging Setup ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NetriNixRecon")

# ---------------------------- Helper Functions ----------------------------
def run_command(cmd, shell=True, cwd=None, timeout=None):
    """Run a command and return output, raise on error."""
    logger.debug(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            logger.warning(f"Command failed (code {result.returncode}): {cmd}\nSTDERR: {result.stderr}")
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {cmd}")
        return "", "TIMEOUT"
    except Exception as e:
        logger.error(f"Exception running command: {cmd} - {e}")
        return "", str(e)

def check_tool_installed(tool_name, config):
    """Check if a tool is installed and accessible."""
    check_cmd = config["check"]
    if config["type"] in ["go", "binary"]:
        out, _ = run_command(check_cmd, shell=True)
        return out != "" and "not found" not in out.lower()
    elif config["type"] == "python_script":
        return os.path.exists(check_cmd)
    return False

def install_tool(tool_name, config):
    """Install a missing tool."""
    logger.info(f"{YELLOW}Installing {tool_name}...{RESET}")
    install_cmd = config["install"]
    # Replace venv placeholder if present
    install_cmd = install_cmd.replace("{venv_pip}", VENV_PIP)
    if config["type"] == "go":
        env = os.environ.copy()
        env["PATH"] = f"{GO_BIN}:{env['PATH']}"
        out, err = run_command(install_cmd, shell=True)
    else:
        out, err = run_command(install_cmd, shell=True)
    if config["type"] == "go" and not check_tool_installed(tool_name, config):
        os.environ["PATH"] = f"{GO_BIN}:{os.environ['PATH']}"
    return check_tool_installed(tool_name, config)

def ensure_all_tools():
    """Ensure all required tools are installed, including the Python venv."""
    os.makedirs(TOOLS_DIR, exist_ok=True)

    # ---- First: create virtual environment if not exists ----
    if not os.path.exists(os.path.join(VENV_DIR, "bin", "python3")):
        logger.info(f"{GREEN}[*] Creating Python virtual environment at {VENV_DIR}...{RESET}")
        run_command(f"{sys.executable} -m venv {VENV_DIR}")
        logger.info(f"{GREEN}[+] Virtual environment ready.{RESET}")

    os.environ["PATH"] = f"{GO_BIN}:{os.environ['PATH']}"  # add go bin to PATH

    for name, config in TOOLS.items():
        if not check_tool_installed(name, config):
            logger.info(f"{name} not found, installing...")
            if not install_tool(name, config):
                logger.error(f"Failed to install {name}. Please install manually.")
                sys.exit(1)
        else:
            logger.debug(f"{name} is already installed.")

    # Nuclei template update
    if check_tool_installed("nuclei", TOOLS["nuclei"]):
        run_command("nuclei -update-templates -silent")

    # Download wordlist
    if not os.path.exists(WORDLIST_PATH):
        logger.info("Downloading common wordlist...")
        run_command(f"wget -q {WORDLIST_URL} -O {WORDLIST_PATH}")

def print_banner():
    print(BANNER)
    print(f"{BOLD}{GREEN}[+] NetriNix Recon Engine v1.0{RESET}")
    print(f"{BOLD}{CYAN}[+] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")

# ---------------------------- Time Estimation ----------------------------
def estimate_time(target):
    logger.info(f"{CYAN}[*] Estimating time for target: {target}{RESET}")
    estimation = {}
    try:
        out, _ = run_command(f"subfinder -d {target} -silent -t 100 -max-time 30", timeout=35)
        subdomains = [s for s in out.splitlines() if s.strip()]
        est_sub = len(subdomains)
    except:
        est_sub = 0
    estimation["subdomains"] = est_sub

    ip_target = target
    try:
        import socket
        ip_target = socket.gethostbyname(target)
    except:
        pass
    nmap_out, _ = run_command(f"nmap -F -T5 --open {ip_target}", timeout=60)
    open_ports = len(re.findall(r"(\d+)/tcp\s+open", nmap_out))
    estimation["open_ports"] = open_ports

    t_nmap = open_ports * 15 + 10
    t_subfinder = est_sub * 0.5
    t_httpx = est_sub * 0.8
    t_gobuster = 100
    t_nuclei = max(est_sub, 1) * 200 / 10
    t_js = est_sub * 3 * 10
    total_sec = t_nmap + t_subfinder + t_httpx + t_gobuster + t_nuclei + t_js

    mins, sec = divmod(int(total_sec), 60)
    hours, mins = divmod(mins, 60)
    time_str = f"{hours}h {mins}m {sec}s" if hours else f"{mins}m {sec}s"
    logger.info(f"{GREEN}Estimated total time: {time_str} (based on {est_sub} subdomains, {open_ports} open ports){RESET}")
    return total_sec, estimation

# ---------------------------- Main Recon Class ----------------------------
class NetriNixRecon:
    def __init__(self, target):
        self.target = target
        self.is_ip = self._is_ip(target)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.outdir = f"recon_{target}_{self.timestamp}"
        os.makedirs(self.outdir, exist_ok=True)
        self.results = {}

    def _is_ip(self, s):
        parts = s.split(".")
        if len(parts) != 4:
            return False
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

    def run_nmap(self):
        logger.info(f"{BLUE}[1/6] Nmap Port Scanning{RESET}")
        ip = self.target if self.is_ip else self.target
        quick_out, _ = run_command(f"nmap -T4 -F --open -oG {self.outdir}/nmap_quick.gnmap {ip}")
        open_ports = []
        with open(f"{self.outdir}/nmap_quick.gnmap") as f:
            for line in f:
                if "Ports:" in line:
                    ports_part = line.split("Ports:")[1].strip()
                    for p in ports_part.split(","):
                        port = p.split("/")[0].strip()
                        if port.isdigit():
                            open_ports.append(port)
        if not open_ports:
            logger.warning("No open ports found, skipping detailed scan.")
            self.results["nmap"] = {"open_ports": [], "output": ""}
            return

        ports_str = ",".join(open_ports)
        logger.info(f"Found open ports: {ports_str}. Running service scan...")
        nmap_cmd = f"nmap -sV -sC -O -p {ports_str} -oN {self.outdir}/nmap_services.txt {ip}"
        run_command(nmap_cmd)
        with open(f"{self.outdir}/nmap_services.txt") as f:
            self.results["nmap"] = {"open_ports": open_ports, "output": f.read()}

    def run_subfinder(self):
        if self.is_ip:
            logger.info("Skipping subdomain discovery for IP target.")
            self.results["subdomains"] = []
            return
        logger.info(f"{BLUE}[2/6] Subdomain Discovery (subfinder){RESET}")
        out, _ = run_command(f"subfinder -d {self.target} -silent -o {self.outdir}/subdomains.txt")
        subdomains = []
        if os.path.exists(f"{self.outdir}/subdomains.txt"):
            with open(f"{self.outdir}/subdomains.txt") as f:
                subdomains = [line.strip() for line in f if line.strip()]
        logger.info(f"Found {len(subdomains)} subdomains.")
        self.results["subdomains"] = subdomains

    def run_httpx(self):
        logger.info(f"{BLUE}[3/6] Probing alive hosts (httpx){RESET}")
        if self.is_ip:
            alive = [f"https://{self.target}", f"http://{self.target}"]
            out, _ = run_command(f"echo '{self.target}' | httpx -silent -title -status-code -o {self.outdir}/alive.txt")
        else:
            if os.path.exists(f"{self.outdir}/subdomains.txt"):
                run_command(f"cat {self.outdir}/subdomains.txt | httpx -silent -title -status-code -o {self.outdir}/alive.txt")
        alive_hosts = []
        if os.path.exists(f"{self.outdir}/alive.txt"):
            with open(f"{self.outdir}/alive.txt") as f:
                alive_hosts = [line.strip() for line in f if line.strip()]
        logger.info(f"Alive hosts: {len(alive_hosts)}")
        self.results["alive_hosts"] = alive_hosts

    def run_js_analysis(self):
        logger.info(f"{BLUE}[4/6] JavaScript Analysis (subjs + linkfinder + secretfinder){RESET}")
        js_files_path = f"{self.outdir}/js_files.txt"
        if self.is_ip:
            urls = [f"https://{self.target}", f"http://{self.target}"]
            subjs_input = "\n".join(urls)
            run_command(f"echo '{subjs_input}' | subjs -o {js_files_path}")
        else:
            run_command(f"cat {self.outdir}/alive.txt | subjs -o {js_files_path}")
        js_urls = []
        if os.path.exists(js_files_path):
            with open(js_files_path) as f:
                js_urls = [line.strip() for line in f if line.strip()]
        logger.info(f"Found {len(js_urls)} JS file URLs.")
        self.results["js_files"] = js_urls

        # Analyze JS with the venv's Python
        endpoints = []
        secrets = []
        def analyze_js(js_url):
            ep, sec = [], []
            # Use VENV_PYTHON to run LinkFinder and SecretFinder
            lf_cmd = f"{VENV_PYTHON} {TOOLS_DIR}/LinkFinder/linkfinder.py -i {js_url} -o cli"
            out_lf, _ = run_command(lf_cmd, timeout=30)
            ep.extend([line.strip() for line in out_lf.splitlines() if line.strip()])

            sf_cmd = f"{VENV_PYTHON} {TOOLS_DIR}/SecretFinder/SecretFinder.py -i {js_url} -o cli"
            out_sf, _ = run_command(sf_cmd, timeout=30)
            sec.extend([line.strip() for line in out_sf.splitlines() if line.strip()])
            return ep, sec

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(analyze_js, url): url for url in js_urls[:20]}
            for future in as_completed(futures):
                try:
                    ep, sc = future.result()
                    endpoints.extend(ep)
                    secrets.extend(sc)
                except Exception as e:
                    logger.warning(f"JS analysis failed for {futures[future]}: {e}")

        with open(f"{self.outdir}/endpoints.txt", "w") as f:
            f.write("\n".join(set(endpoints)))
        with open(f"{self.outdir}/secrets.txt", "w") as f:
            f.write("\n".join(set(secrets)))
        self.results["endpoints"] = endpoints
        self.results["secrets"] = secrets

    def run_gobuster(self):
        logger.info(f"{BLUE}[5/6] Directory Brute Force (gobuster){RESET}")
        base_url = None
        for host in self.results.get("alive_hosts", []):
            url = host.split(" ")[0]
            if url.startswith("http"):
                base_url = url
                break
        if not base_url:
            base_url = f"http://{self.target}"
        logger.info(f"Target URL: {base_url}")
        gobuster_cmd = f"gobuster dir -u {base_url} -w {WORDLIST_PATH} -o {self.outdir}/gobuster.txt -q"
        run_command(gobuster_cmd)
        if os.path.exists(f"{self.outdir}/gobuster.txt"):
            with open(f"{self.outdir}/gobuster.txt") as f:
                self.results["gobuster"] = f.read()

    def run_nuclei(self):
        logger.info(f"{BLUE}[6/6] Vulnerability Scanning (nuclei){RESET}")
        if os.path.exists(f"{self.outdir}/alive.txt"):
            run_command(f"nuclei -l {self.outdir}/alive.txt -t ~/nuclei-templates/ -o {self.outdir}/nuclei.txt -silent -stats")
        if os.path.exists(f"{self.outdir}/nuclei.txt"):
            with open(f"{self.outdir}/nuclei.txt") as f:
                self.results["nuclei"] = f.read()

    def generate_html_report(self):
        logger.info(f"{GREEN}Generating HTML report...{RESET}")
        report_path = f"{self.outdir}/report.html"
        nmap_ports = self.results.get("nmap", {}).get("open_ports", [])
        nmap_out = self.results.get("nmap", {}).get("output", "")
        subdomains = self.results.get("subdomains", [])
        alive = self.results.get("alive_hosts", [])
        js_files = self.results.get("js_files", [])
        endpoints = self.results.get("endpoints", [])
        secrets = self.results.get("secrets", [])
        gobuster = self.results.get("gobuster", "")
        nuclei = self.results.get("nuclei", "")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetriNix Recon Report - {self.target}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #0a192f; color: #ccd6f6; }}
        .card {{ background-color: #112240; border: none; }}
        .card-header {{ background-color: #1d3557; color: #64ffda; font-weight: bold; }}
        .badge {{ font-size: 0.9em; }}
        pre {{ background-color: #0a192f; color: #a8b2d1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .header-bg {{ background: linear-gradient(135deg, #1d3557 0%, #0a192f 100%); }}
        .text-netrinix {{ color: #64ffda; }}
    </style>
</head>
<body>
<div class="container-fluid py-4">
    <div class="header-bg text-center p-4 mb-4 rounded">
        <h1 class="text-netrinix">NetriNix Recon Report</h1>
        <h5>Target: <span class="text-light">{self.target}</span></h5>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Srimant Kumar - netrinix.com</p>
    </div>

    <div class="row g-3">
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{len(nmap_ports)}</h3><p>Open Ports</p></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{len(subdomains)}</h3><p>Subdomains</p></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{len(alive)}</h3><p>Alive Hosts</p></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{len(js_files)}</h3><p>JS Files</p></div></div></div>
    </div>

    <div class="card my-4">
        <div class="card-header">Nmap Service Scan</div>
        <div class="card-body"><pre>{nmap_out if nmap_out else "No open ports found."}</pre></div>
    </div>

    <div class="card my-4">
        <div class="card-header">Subdomains ({len(subdomains)})</div>
        <div class="card-body"><pre>{chr(10).join(subdomains) if subdomains else "None"}</pre></div>
    </div>

    <div class="card my-4">
        <div class="card-header">Alive Hosts (httpx)</div>
        <div class="card-body"><pre>{chr(10).join(alive) if alive else "None"}</pre></div>
    </div>

    <div class="card my-4">
        <div class="card-header">JavaScript Endpoints ({len(endpoints)})</div>
        <div class="card-body"><pre style="max-height:300px;">{chr(10).join(endpoints[:100]) if endpoints else "None"}</pre></div>
    </div>
    <div class="card my-4">
        <div class="card-header">Secrets Found ({len(secrets)})</div>
        <div class="card-body"><pre style="max-height:300px;">{chr(10).join(secrets[:100]) if secrets else "None"}</pre></div>
    </div>

    <div class="card my-4">
        <div class="card-header">Directory Brute Force</div>
        <div class="card-body"><pre>{gobuster if gobuster else "No results."}</pre></div>
    </div>

    <div class="card my-4">
        <div class="card-header">Nuclei Vulnerabilities</div>
        <div class="card-body"><pre>{nuclei if nuclei else "No critical findings."}</pre></div>
    </div>

    <div class="text-center mt-4 text-muted">
        <small>Powered by NetriNix Recon Engine | https://netrinix.com</small>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        with open(report_path, "w") as f:
            f.write(html)
        logger.info(f"{GREEN}Report saved: {report_path}{RESET}")
        return report_path

    def full_recon(self):
        phases = [
            self.run_nmap,
            self.run_subfinder,
            self.run_httpx,
            self.run_js_analysis,
            self.run_gobuster,
            self.run_nuclei
        ]
        for phase in phases:
            try:
                phase()
            except Exception as e:
                logger.error(f"Error in {phase.__name__}: {e}")
        self.generate_html_report()

# ---------------------------- Main ----------------------------
def main():
    print_banner()
    parser = argparse.ArgumentParser(description="NetriNix Recon Engine - Full automated reconnaissance")
    parser.add_argument("target", help="Target domain or IP address")
    parser.add_argument("--skip-estimate", action="store_true", help="Skip time estimation")
    args = parser.parse_args()
    target = args.target

    ensure_all_tools()

    if not args.skip_estimate:
        total_sec, _ = estimate_time(target)
        while True:
            choice = input(f"{YELLOW}Proceed with full recon? (y/n): {RESET}").lower()
            if choice in ['y', 'yes']:
                break
            elif choice in ['n', 'no']:
                logger.info("Aborted by user.")
                sys.exit(0)

    recon = NetriNixRecon(target)
    recon.full_recon()
    report = f"{recon.outdir}/report.html"
    logger.info(f"{BOLD}{GREEN}Recon complete! Open {report} in your browser.{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Interrupted by user.{RESET}")
        sys.exit(1)
