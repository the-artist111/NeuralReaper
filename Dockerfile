FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MAX_TOOL_RUNTIME=180

# ── Core tools (all confirmed in Ubuntu 24.04 repos) ────────
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    git curl wget ruby ruby-dev \
    nmap masscan \
    nikto \
    dirb gobuster \
    sqlmap \
    whois dnsutils \
    openssl \
    traceroute iputils-ping net-tools \
    libpcap-dev \
    libcap2-bin \
    build-essential \
    gdb \
    chkrootkit rkhunter lynis \
    afl++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Install wpscan via gem ───────────────────────────────────
RUN gem install wpscan --no-document

# ── Install ffuf via direct binary download ─────────────────
RUN wget -q https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_linux_amd64.tar.gz \
    -O /tmp/ffuf.tar.gz \
    && tar -xzf /tmp/ffuf.tar.gz -C /usr/local/bin ffuf \
    && rm /tmp/ffuf.tar.gz

# ── Install exploitdb (searchsploit) ────────────────────────
RUN git clone --depth 1 https://gitlab.com/exploit-database/exploitdb.git /opt/exploitdb \
    && ln -sf /opt/exploitdb/searchsploit /usr/local/bin/searchsploit \
    && cp /opt/exploitdb/.searchsploit_rc /root/.searchsploit_rc

# ── Install Go ──────────────────────────────────────────────
RUN wget -q https://go.dev/dl/go1.22.3.linux-amd64.tar.gz -O /tmp/go.tar.gz \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm /tmp/go.tar.gz
ENV PATH="/usr/local/go/bin:$PATH"

# ── Install Nuclei ──────────────────────────────────────────
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest \
    && mv /root/go/bin/nuclei /usr/local/bin/nuclei

# ── Pull Nuclei templates ───────────────────────────────────
RUN nuclei -update-templates -silent || true

# ── Install OSV-Scanner (Google) — supply-chain dependency audit ──
RUN go install github.com/google/osv-scanner/cmd/osv-scanner@latest \
    && mv /root/go/bin/osv-scanner /usr/local/bin/osv-scanner

# ── Install XSStrike ────────────────────────────────────────
RUN git clone --depth 1 https://github.com/s0md3v/XSStrike /opt/XSStrike \
    && pip3 install --break-system-packages -r /opt/XSStrike/requirements.txt

# ── Python venv for MCP server + AD toolchain ───────────────
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY server.py /app/server.py

# ── Non-root user ───────────────────────────────────────────
RUN useradd -m -s /bin/bash pentester \
    && chown -R pentester:pentester /app /opt/venv \
    && cp -r /root/.local /home/pentester/.local 2>/dev/null || true \
    && cp /root/.searchsploit_rc /home/pentester/.searchsploit_rc 2>/dev/null || true \
    && mkdir -p /scan && chown pentester:pentester /scan \
    && chown -R pentester:pentester /home/pentester

# ── Raw socket caps ─────────────────────────────────────────
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || true \
    && setcap cap_net_raw,cap_net_admin+eip /usr/bin/masscan 2>/dev/null || true

USER pentester
WORKDIR /app

ENTRYPOINT ["python3", "/app/server.py"]
