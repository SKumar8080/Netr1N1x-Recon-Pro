<p align="center">
  <img src="data/logo.png" alt="NetriNix Recon Engine" width="200"/>
</p>

<h1 align="center">⚡ NetriNix Recon Engine ⚡</h1>
<h3 align="center"><i>All-in-One Automated Reconnaissance & Vulnerability Scanning Framework</i></h3>

<p align="center">
  <a href="https://netrinix.com"><img src="https://img.shields.io/badge/Owner-Srimant%20Kumar-blue?style=for-the-badge&logo=github" alt="Owner"/></a>
  <a href="https://netrinix.com"><img src="https://img.shields.io/badge/Academy-NetriNix%20Academy-red?style=for-the-badge&logo=google-chrome" alt="Academy"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-yellow?style=for-the-badge&logo=python" alt="Python"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/></a>
  <a href="https://github.com/netrinix/netrinix-recon/stargazers"><img src="https://img.shields.io/github/stars/netrinix/netrinix-recon?style=for-the-badge" alt="Stars"/></a>
</p>

<p align="center">
  <img src="data/demo.gif" alt="Demo" width="700"/>
</p>

---

## 🚀 About NetriNix Recon Engine

**NetriNix Recon Engine** is a **professional‑grade, fully automated reconnaissance and enumeration framework** designed for penetration testers, bug bounty hunters, and security researchers. It intelligently chains together industry‑standard open‑source tools to discover subdomains, open ports, live hosts, JavaScript endpoints, secrets, hidden directories, and vulnerabilities – all with a single command.

The engine not only runs the recon but also produces a **beautiful, interactive HTML report** that can be opened in any browser for detailed analysis.

### ✨ Key Highlights

- ✅ **Zero‑touch setup** – automatically installs missing tools into an isolated environment.
- 🧠 **Smart time estimator** – performs a quick pre‑scan and tells you exactly how long the full recon will take.
- 🔗 **Deep chaining** – output of one phase feeds the next (e.g., live hosts → JS analysis → secrets).
- 📊 **Professional HTML report** – dark‑themed, with summary cards, collapsible sections, and all findings.
- 🐍 **Isolated Python venv** – LinkFinder & SecretFinder run inside their own virtual environment.
- 🌐 **Supports domain & IP targets** – adapts its workflow accordingly.

---

## 🛠️ Tools Integrated

| Category               | Tools Used                                                                 |
|------------------------|----------------------------------------------------------------------------|
| Port Scanning          | `nmap` (quick + service/OS scan)                                           |
| Subdomain Enumeration  | `subfinder`                                                                |
| Alive Host Probing     | `httpx`                                                                    |
| JS File Discovery      | `subjs`                                                                    |
| Endpoint Extraction    | `LinkFinder`                                                               |
| Secret Discovery       | `SecretFinder`                                                             |
| Directory Brute‑force  | `gobuster`                                                                 |
| Vulnerability Scanning | `nuclei`                                                                   |
| Historical URLs        | `waybackurls` (optional, for future phases)                                |

All tools are automatically installed (Go tools via `go install`, Python tools inside a dedicated `venv`).

---

## 📸 Screenshots

<p align="center">
  <img src="data/terminal.png" alt="Terminal" width="600"/>
  <br/>
  <em>CLI with colorful banner & live time estimation</em>
</p>

<p align="center">
  <img src="data/report_summary.png" alt="HTML Report Summary" width="600"/>
  <br/>
  <em>Interactive HTML report – summary cards</em>
</p>

<p align="center">
  <img src="data/report_nuclei.png" alt="Nuclei Findings" width="600"/>
  <br/>
  <em>Vulnerability findings section</em>
</p>

> 🔜 **Video demo** coming soon – place your video file in `data/demo.mp4`.

---

## 📦 Installation

NetriNix Recon Engine is a single Python script – no complex setup required. It will create its own virtual environment and download all necessary tools automatically.

```bash
git clone https://github.com/netrinix/netrinix-recon.git
cd netrinix-recon
python3 netrinix_recon.py --help


Requirements

    Python 3.8+ (with venv module)

    Go (for Go‑based tools – subfinder, httpx, nuclei, etc.)

    Git (for cloning Python tools)

    wget (for downloading wordlist)

    Linux (tested on Debian/Ubuntu; macOS may work with minor tweaks)

    The script will attempt to sudo apt-get install nmap if missing, so ensure your user has sudo privileges.

⚡ Usage
bash

python3 netrinix_recon.py <target> [--skip-estimate]

Examples
bash

# Full recon on a domain
python3 netrinix_recon.py example.com

# Skip the time estimation and start immediately
python3 netrinix_recon.py example.com --skip-estimate

# Recon on an IP address
python3 netrinix_recon.py 192.168.1.1

Workflow

    Tool Check & Install – verifies/installs all dependencies.

    Time Estimation (optional) – quick subfinder + nmap to give an ETA.

    Nmap – fast port discovery → service/OS scan on open ports.

    Subfinder – passive subdomain enumeration.

    httpx – probes all subdomains for live web servers.

    JS Analysis – extracts JS files → endpoints & secrets.

    Gobuster – directory brute‑force using SecLists common.txt.

    Nuclei – runs vulnerability templates against live hosts.

    HTML Report – generates report.html with all findings.

All intermediate data is stored in recon_<target>_<timestamp>/.
📁 Output Structure
text

recon_example.com_20250315_143000/
├── alive.txt               # httpx live hosts
├── subdomains.txt          # discovered subdomains
├── nmap_quick.gnmap        # Nmap quick scan (greppable)
├── nmap_services.txt       # Nmap service/OS scan
├── js_files.txt            # discovered JavaScript URLs
├── endpoints.txt           # endpoints from LinkFinder
├── secrets.txt             # secrets from SecretFinder
├── gobuster.txt            # directory brute‑force results
├── nuclei.txt              # Nuclei vulnerability findings
└── report.html             # 🖥️ Final interactive report

🧪 Under the Hood

    Virtual Environment – on first run, the script creates netrinix_tools/venv and installs LinkFinder & SecretFinder there, ensuring no conflict with system Python packages.

    Thread Pool – JS analysis uses a ThreadPoolExecutor to process multiple JS files concurrently.

    Smart Chaining – subfinder output feeds httpx, which feeds subjs and nuclei, maximizing automation.

    Fully Configurable – you can easily tweak tool paths, wordlists, and thread counts in the source code.

🤝 Contributing

We welcome contributions! Feel free to open issues or pull requests for new features, bug fixes, or tool integrations.

    Fork the repository

    Create your feature branch (git checkout -b feature/awesome-feature)

    Commit your changes

    Push to the branch

    Open a Pull Request

📜 License

This project is licensed under the MIT License – see the LICENSE file for details.
👤 Author
<p align="center"> <b>Srimant Kumar</b><br> Founder & Trainer at <a href="https://netrinix.com">NetriNix Academy</a><br> <a href="https://netrinix.com">https://netrinix.com</a> </p><p align="center"> <sub>Built with ❤️ for the security community.</sub> </p> ```
