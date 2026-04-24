# 5G Network Architecture Report

## Table of Contents
1. [Overall Telecom Architecture](#1-overall-telecom-architecture)
2. [5G SA Network Instantiation](#2-5g-sa-network-instantiation)
3. [End-to-End Ping Test to Google](#3-end-to-end-ping-test-to-google)
4. [Packet Capture — Docker Bridge (All Traffic from Host)](#4-packet-capture--docker-bridge-all-traffic-from-host)
5. [Packet Capture — Per-Interface Inside Containers](#5-packet-capture--per-interface-inside-containers)

---

## 1. Overall Telecom Architecture

### 1.0 Getting docker_open5gs from GitHub

The entire stack is managed from the [herlesupreeth/docker_open5gs](https://github.com/herlesupreeth/docker_open5gs) repository.

#### Prerequisites

| Requirement | Minimum Version |
|-------------|----------------|
| OS | Ubuntu 20.04 / 22.04 LTS |
| docker-ce | 22.0.5 or above |
| docker compose (plugin) | 2.14 or above |
| Kernel modules | `ip_tables`, `nf_nat`, `xt_MASQUERADE` (usually pre-loaded) |

```bash
# Install Docker CE (if not already installed)
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group (re-login after this)
sudo usermod -aG docker $USER
```

#### Clone the Repository

```bash
git clone https://github.com/herlesupreeth/docker_open5gs
cd docker_open5gs
```

#### Option A — Pull Pre-built Images from GHCR (Faster)

```bash
# Core 5G/EPC base image
docker pull ghcr.io/herlesupreeth/docker_open5gs:master
docker tag  ghcr.io/herlesupreeth/docker_open5gs:master docker_open5gs

# Metrics / Grafana
docker pull ghcr.io/herlesupreeth/docker_metrics:master
docker tag  ghcr.io/herlesupreeth/docker_metrics:master docker_metrics

# UERANSIM (gNB + UE simulator)
docker pull ghcr.io/herlesupreeth/docker_ueransim:master
docker tag  ghcr.io/herlesupreeth/docker_ueransim:master docker_ueransim

# IMS components (needed for VoNR / VoLTE)
docker pull ghcr.io/herlesupreeth/docker_pyhss:master
docker tag  ghcr.io/herlesupreeth/docker_pyhss:master docker_pyhss

docker pull ghcr.io/herlesupreeth/docker_kamailio:master
docker tag  ghcr.io/herlesupreeth/docker_kamailio:master docker_kamailio

# Optional: srsRAN, OCS, eUPF, OpenSIPS, ePDG, SWu
docker pull ghcr.io/herlesupreeth/docker_srsran:master
docker tag  ghcr.io/herlesupreeth/docker_srsran:master docker_srsran
```

#### Option B — Build Images from Source

```bash
cd docker_open5gs

# 1. open5gs EPC / 5GC (mandatory)
cd base
docker build --no-cache --force-rm -t docker_open5gs .

# 2. Kamailio IMS (needed for VoNR / VoLTE)
cd ../ims_base
docker build --no-cache --force-rm -t docker_kamailio .

# 3. UERANSIM — 5G gNB + UE simulator
cd ../ueransim
docker build --no-cache --force-rm -t docker_ueransim .

# 4. srsRAN_4G — eNB + 4G/5G UE (ZMQ simulation)
cd ../srslte
docker build --no-cache --force-rm -t docker_srslte .

# 5. srsRAN_Project — 5G gNB
cd ../srsran
docker build --no-cache --force-rm -t docker_srsran .

# 6. eUPF (alternative UPF)
cd ../eupf
docker build --no-cache --force-rm -t docker_eupf .
```

#### Configure .env Before First Run

```bash
cd docker_open5gs

# Edit the environment file — minimum required changes for a single-host SA setup:
#   DOCKER_HOST_IP  →  set to the host's reachable IP (currently 172.29.163.51)
#   MCC / MNC / TAC →  match your SIM / UE config (currently 001 / 01 / 1)
#   UE1_IMSI / UE1_KI / UE1_OP → match your subscriber credentials
nano .env

# Enable IP forwarding on the host (required for UPF NAT)
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Optional: disable ufw to avoid interfering with docker networking
sudo ufw disable
```

---

### Network Configuration Summary

| Parameter | Value |
|-----------|-------|
| MCC | 001 |
| MNC | 01 |
| TAC | 1 |
| PLMN | 001-01 |
| Docker Network | `172.22.0.0/24` |
| Docker Host IP | `172.29.163.51` |
| UE Internet APN Subnet | `192.168.100.0/24` |
| UE IMS APN Subnet | `192.168.101.0/24` |

---

### 1.1 Complete Network Element IP Map

| Component | Container Name | IP Address | Key Ports / Interfaces |
|-----------|---------------|------------|------------------------|
| MongoDB | mongo | `172.22.0.2` | 27017/tcp, 27017/udp |
| WebUI | webui | `172.22.0.26` | 9999/tcp |
| **5G Core (SA)** | | | |
| NRF | nrf | `172.22.0.12` | 7777/tcp (SBI) |
| SCP | scp | `172.22.0.35` | 7777/tcp (SBI) |
| AMF | amf | `172.22.0.10` | 38412/sctp (N2), 7777/tcp (SBI), 9091/tcp (metrics) |
| SMF | smf | `172.22.0.7` | 8805/udp (N4/PFCP), 7777/tcp (SBI), 9091/tcp (metrics) |
| UPF | upf | `172.22.0.8` | 2152/udp (N3/GTP-U), 8805/udp (N4/PFCP), 9091/tcp (metrics) |
| AUSF | ausf | `172.22.0.11` | 7777/tcp (SBI) |
| UDM | udm | `172.22.0.13` | 7777/tcp (SBI) |
| UDR | udr | `172.22.0.14` | 7777/tcp (SBI) |
| PCF | pcf | `172.22.0.27` | 7777/tcp (SBI), 9091/tcp (metrics) |
| BSF | bsf | `172.22.0.29` | 7777/tcp (SBI) |
| NSSF | nssf | `172.22.0.28` | 7777/tcp (SBI) |
| **4G/EPC** | | | |
| HSS (Open5GS) | hss | `172.22.0.3` | S6a/Diameter |
| MME | mme | `172.22.0.9` | S1-AP/SCTP, S6a/Diameter, S11/GTP-C |
| SGW-C | sgwc | `172.22.0.5` | S11/GTP-C, Sxa/PFCP |
| SGW-U | sgwu | `172.22.0.6` | S1-U/GTP-U, Sxa/PFCP |
| PCRF | pcrf | `172.22.0.4` | 3873/tcp (Gx/Diameter) |
| **IMS** | | | |
| DNS (IMS) | dns | `172.22.0.15` | 53/udp, 53/tcp |
| pyHSS | pyhss | `172.22.0.18` | 3875/tcp (Cx/Diameter) |
| I-CSCF | icscf | `172.22.0.19` | 3869/tcp (SIP/Diameter) |
| S-CSCF | scscf | `172.22.0.20` | 3870/tcp (SIP/Diameter) |
| P-CSCF | pcscf | `172.22.0.21` | 3871/tcp (SIP) |
| IBCF | ibcf | `172.22.0.140` | SIP |
| RTPENGINE | rtpengine | `172.22.0.16` | RTP relay |
| MySQL | mysql | `172.22.0.17` | 3306/tcp |
| OCS | ocs | `172.22.0.40` | 3872/tcp (Gy/Diameter) |
| SMSC | smsc | `172.22.0.33` | SMS |
| **RAN / UE Simulators** | | | |
| NR gNB (UERANSIM) | nr_gnb | `172.22.0.23` | 38412/sctp (N2), 2152/udp (N3), 4997/udp |
| NR UE (UERANSIM) | nr_ue | `172.22.0.24` | 4997/udp |
| SRS eNB | srsenb | `172.22.0.22` | S1-AP/SCTP |
| SRS gNB | srsgnb | `172.22.0.37` | 38412/sctp, 2152/udp |
| SRS UE | srsue | `172.22.0.34` | – |
| OAI eNB | oaienb | `172.22.0.25` | S1-AP/SCTP |
| **Monitoring** | | | |
| Prometheus | metrics | `172.22.0.36` | 9090/tcp |
| Grafana | grafana | `172.22.0.39` | 3000/tcp |
| **Other** | | | |
| OsmoMSC | osmomsc | `172.22.0.31` | A/MAP |
| OsmoHLR | osmohlr | `172.22.0.32` | Mw/MAP |
| OsmoePDG | osmoepdg | `172.22.0.41` | SWu |
| SWu Client | swu_client | `172.22.0.42` | IKEv2 |

---

### 1.2 Complete Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          Docker Network: docker_open5gs_default  172.22.0.0/24                   ║
╠══════════════════════════════════════════════════════╦═══════════════════════════════════════════╣
║              5G SA CORE (3GPP Release 16)            ║           IMS / VoNR Subsystem            ║
║                                                      ║                                           ║
║  ┌─────────┐  Nnrf  ┌─────────┐  Nscp  ┌─────────┐   ║ ┌───────────────────────────────────┐     ║
║  │   NRF   │◄──────►│   SCP   │◄──────►│  NSSF   │   ║ │  P-CSCF  172.22.0.21 :3871        │     ║
║  │.12:7777 │        │.35:7777 │        │.28:7777 │   ║ │  I-CSCF  172.22.0.19 :3869        │     ║
║  └────┬────┘        └─────────┘        └─────────┘   ║ │  S-CSCF  172.22.0.20 :3870        │     ║
║       │Nnrf                                          ║ │  IBCF    172.22.0.140             │     ║
║  ┌────┼────────────────────────────────────────┐     ║ │  DNS     172.22.0.15              │     ║
║  │    ▼        SBI (HTTP/2, :7777)             │     ║ │  pyHSS   172.22.0.18 :3875        │     ║
║  │  ┌──────┐  N12  ┌──────┐  N13  ┌──────┐     │     ║ │  RTPENG  172.22.0.16              │     ║
║  │  │ AUSF │◄─────►│ UDM  │◄─────►│ UDR  │     │     ║ └───────────────────────────────────┘     ║
║  │  │  .11 │       │  .13 │       │  .14 │     │     ║                                           ║
║  │  └──────┘       └──────┘       └──────┘     │     ╠═══════════════════════════════════════════╣
║  │       N8↕           N10↕                    │     ║           4G / EPC Subsystem              ║
║  │  ┌──────┐  N15  ┌──────┐  N7   ┌──────┐     │     ║                                           ║
║  │  │ AMF  │◄─────►│ PCF  │◄─────►│ SMF  │     │     ║  ┌──────┐  S6a  ┌──────┐  Gx  ┌──────┐    ║
║  │  │  .10 │  N11  │  .27 │  N4↕  │  .7  │     │     ║  │ HSS  │◄─────►│ MME  │◄────►│ PCRF │    ║
║  │  │:38412│◄──────┤       │       │:8805 │    │     ║  │  .3  │       │  .9  │      │ .4   │    ║
║  │  │:7777 │       └──────┘       │:7777 │     │     ║  └──────┘       └──┬───┘      └──────┘    ║
║  │  └──┬───┘  N22  ┌──────┐       └──┬───┘     │     ║                    │S11                   ║
║  │     │◄──────────│ NSSF │          │N4       │     ║  ┌──────┐  Sxa  ┌──┴───┐                  ║
║  │     │           │  .28 │       ┌──▼───┐     │     ║  │SGW-U │◄─────►│SGW-C │                  ║
║  │     │           └──────┘       │ UPF  │     │     ║  │  .6  │       │  .5  │                  ║
║  │     │           ┌──────┐       │  .8  │     │     ║  │:2152 │       └──────┘                  ║
║  │     │           │  BSF │       │:2152 │     │     ║  └──────┘                                 ║
║  │     │           │  .29 │       │:8805 │     │     ╠═══════════════════════════════════════════╣
║  │     │           └──────┘       └──┬───┘     │     ║              Monitoring                   ║
║  └─────┼──────────────────────────┼──┘         │     ║                                           ║
║        │N2 (NGAP/SCTP :38412)     │N3 (GTP-U)  ║     ║  Prometheus  172.22.0.36 :9090            ║
╚════════╪══════════════════════════╪════════════╩═════║  Grafana     172.22.0.39 :3000            ║
         │                          │                  ╚═══════════════════════════════════════════╝
╔════════╪══════════════════════════╪═══════════════════════════════════════════════════════════════╗
║   RAN  │                          │ GTP-U                                                         ║
║   ┌────┴──────┐                   │                                                               ║
║   │  nr_gnb   │───────────────────┘                                                               ║
║   │172.22.0.23│  N2:38412/sctp  N3:2152/udp  Radio:4997/udp                                       ║
║   └─────┬─────┘                                                                                   ║
║         │ Uu (Radio Link Sim / 4997/udp)                                                          ║
║   ┌─────┴─────┐                                                                                   ║
║   │   nr_ue   │  IMSI: 001011234567895   SUPI: imsi-001011234567895                               ║
║   │172.22.0.24│  KI: 8baf473f2f8fd09487cccbd7097c6862                                             ║
║   └───────────┘  Slice SST=1  APN=internet  UE-IP: 192.168.100.x (via ogstun)                     ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

### 1.3 Interface Reference Table (5G SA)

| Interface | From → To | Protocol | Port | Description |
|-----------|-----------|----------|------|-------------|
| **Uu** | UE ↔ gNB | Radio Link Sim (UDP) | 4997 | Air interface |
| **N1** | UE ↔ AMF | NAS (via gNB tunnel) | – | Registration, session management |
| **N2** | gNB ↔ AMF | NGAP / SCTP | 38412 | RAN–Core control plane |
| **N3** | gNB ↔ UPF | GTP-U / UDP | 2152 | User-plane data tunnel |
| **N4** | SMF ↔ UPF | PFCP / UDP | 8805 | Session rules, QoS enforcement |
| **N7** | SMF ↔ PCF | SBI (HTTP/2) | 7777 | Policy control |
| **N8** | AMF ↔ UDM | SBI (HTTP/2) | 7777 | Subscriber data |
| **N10** | SMF ↔ UDM | SBI (HTTP/2) | 7777 | Session management subscription |
| **N11** | AMF ↔ SMF | SBI (HTTP/2) | 7777 | PDU session setup |
| **N12** | AMF ↔ AUSF | SBI (HTTP/2) | 7777 | Authentication |
| **N13** | AUSF ↔ UDM | SBI (HTTP/2) | 7777 | Authentication credentials |
| **N15** | AMF ↔ PCF | SBI (HTTP/2) | 7777 | UE policy |
| **N22** | AMF ↔ NSSF | SBI (HTTP/2) | 7777 | Network slice selection |
| **N27** | SCP ↔ NRF | SBI (HTTP/2) | 7777 | NF discovery proxy |
| **Nnrf** | All NFs ↔ NRF | SBI (HTTP/2) | 7777 | NF registration & discovery |

---

## 2. 5G SA Network Instantiation

### 2.1 Container Dependency Chain

The following shows the boot order enforced by `sa-deploy.yaml` combined with the RAN containers from `nr-gnb.yaml` and `nr-ue.yaml`:

```
MongoDB
   └─► WebUI
NRF
   └─► SCP
         ├─► AUSF ──────────────────────────────────────┐
         ├─► UDR (+ MongoDB)                            │
         ├─► UDM                                        │
         ├─► PCF  (+ MongoDB) ─────────────────────┐   │
         ├─► BSF  (+ MongoDB)                       │   │
         ├─► NSSF (+ MongoDB)                       │   │
         └─► AMF ◄──── (depends: AUSF, UDM, UDR, PCF, BSF)
                └─► SMF (+ AMF)
                       └─► UPF (+ SMF)

[External network: docker_open5gs_default]
         └─► nr_gnb  (nr-gnb.yaml) ── joins existing network
                └─► nr_ue  (nr-ue.yaml) ── joins existing network
```

---

### 2.2 Full 5G SA Call Flow Diagram

```
  nr_ue                  nr_gnb               AMF                 AUSF / UDM / UDR       SMF / UPF
172.22.0.24           172.22.0.23          172.22.0.10            .11 / .13 / .14      .7 / .8
    │                     │                    │                        │                   │
    │──── Uu (RRC) ───────►                    │                        │                   │
    │      Radio Link Simulation (UDP:4997)     │                        │                   │
    │                     │                    │                        │                   │
    │                     │── N2 NGAP Init ───►│  (SCTP :38412)         │                   │
    │                     │  NG Setup Request  │                        │                   │
    │                     │◄── NG Setup Resp ──│                        │                   │
    │                     │                    │                        │                   │
    │── NAS: Registration ►── N2 Init UE ─────►│                        │                   │
    │   Request (IMSI:     │  (NGAP/SCTP)      │                        │                   │
    │   001011234567895)   │                   │── Nnausf_UEAuth ───────►│ (AUSF HTTP/2:7777)│
    │                     │                    │◄── Auth Vector ─────────│                   │
    │◄─ NAS: Auth Req ────◄── N2 DL NAS ──────│                        │                   │
    │── NAS: Auth Resp ───►── N2 UL NAS ──────►│                        │                   │
    │                     │                    │── Nudm_UECM_Reg ───────►│ (UDM HTTP/2:7777) │
    │                     │                    │── Nudm_SDM_Get ─────────►│                   │
    │                     │                    │◄── Subscription Data ───│                   │
    │◄─ NAS: Reg Accept ──◄── N2 DL NAS ──────│                        │                   │
    │── NAS: Reg Complete ►── N2 UL NAS ──────►│                        │                   │
    │                     │                    │                        │                   │
    │── NAS: PDU Session  ►── N2 UL NAS ──────►│  PDU Session           │                   │
    │   Establish (APN:   │  EstabRequest      │── N11 Nsmf_PDU ──────────────────────────►│
    │   internet, SST:1)  │                    │   SessionCreate        │                   │
    │                     │                    │                        │── N4 PFCP ──────►│UPF
    │                     │                    │                        │   Session Estab  │.8:8805
    │                     │                    │                        │                  │ creates
    │                     │                    │                        │                  │ ogstun
    │                     │                    │                        │                  │ 192.168.100.x
    │                     │                    │◄──────────────── N11 PDU Session Resp ────│
    │◄─ NAS: PDU Accept ──◄── N2 DL NAS+      │                                           │
    │   (UE-IP assigned)  │   PDU Sess Res     │                                           │
    │                     │                    │                                           │
    │                     │── N3 GTP-U Tunnel established ────────────────────────────────►│
    │                     │   (UDP :2152, GNB:172.22.0.23 ←→ UPF:172.22.0.8)              │
    │                     │                                                                 │
    │◄════════════════ User Plane Data Path (encapsulated in GTP-U) ══════════════════════►│
    │                192.168.100.x ════════════════ GTP-U ══════════════ ogstun ─► Internet│
```

---

### 2.3 Network Interfaces & Bindings per Container

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        docker_open5gs_default  172.22.0.0/24                     │
│                                                                                  │
│  ┌──────────────────────┐          ┌──────────────────────────────────────────┐  │
│  │     nr_gnb           │          │             AMF                          │  │
│  │  172.22.0.23         │          │          172.22.0.10                     │  │
│  │                      │ N2/NGAP  │                                          │  │
│  │  eth0:172.22.0.23 ───┼──────────┼─► eth0:172.22.0.10  :38412/sctp         │  │
│  │  (SCTP :38412 out)   │          │                                          │  │
│  │  (UDP  :2152  out)   │ N3/GTP-U │  SBI: http://172.22.0.10:7777           │  │
│  │  (UDP  :4997  in)    │          └──────────────────────────────────────────┘  │
│  └──────────┬───────────┘                                                        │
│             │ N3 GTP-U (UDP:2152)         ┌──────────────────────────────────┐   │
│             │                             │            UPF                   │   │
│             └─────────────────────────────┼─► eth0:172.22.0.8  :2152/udp    │   │
│                                           │   ogstun (tun)  192.168.100.0/24 │   │
│  ┌──────────────────────┐                 │   ogstun2(tun)  192.168.101.0/24 │   │
│  │     nr_ue            │                 │   N4/PFCP: :8805/udp             │   │
│  │  172.22.0.24         │                 └──────────────────────────────────┘   │
│  │                      │                                                        │
│  │  eth0:172.22.0.24    │  Uu simulation  ┌──────────────────────────────────┐   │
│  │  (UDP :4997 in/out)  │◄───────────────►│            SMF                   │   │
│  │  uesimtun0 assigned  │  to nr_gnb      │         172.22.0.7               │   │
│  │  192.168.100.x       │  172.22.0.23    │   N4/PFCP: :8805/udp             │   │
│  └──────────────────────┘                 │   SBI: http://172.22.0.7:7777    │   │
│                                           └──────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Step-by-Step Instantiation Commands

```bash
# Step 1 — Build base images (run from docker_open5gs/)
docker compose -f sa-deploy.yaml build

# Step 2 — Start the 5G SA core
docker compose -f sa-deploy.yaml up -d

# Step 3 — Verify all core NFs are running
docker compose -f sa-deploy.yaml ps

# Step 4 — Add a subscriber via WebUI (http://HOST:9999)
#   Or use the add-subscriber script:
#   IMSI : 001011234567895
#   KI   : 8baf473f2f8fd09487cccbd7097c6862
#   OP   : 11111111111111111111111111111111
#   AMF  : 8000

# Step 5 — Start the gNB (attaches to existing core network)
docker compose -f nr-gnb.yaml up -d

# Step 6 — Start the UE
docker compose -f nr-ue.yaml up -d

# Step 7 — Verify UE registration
docker logs nr_ue | grep -E "PDU|registered|connected"
```

---

### 2.5 Port Exposure Summary (Host ↔ Container)

| Host Port | Container Port | Protocol | Container | Purpose |
|-----------|---------------|----------|-----------|---------|
| `9999` | `9999` | TCP | webui | Open5GS Web UI |
| `38412` | `38412` | SCTP | amf | N2 (NGAP) – gNB registration |
| `2152` | `2152` | UDP | upf | N3 (GTP-U) – user-plane data |
| `9090` | `9090` | TCP | metrics | Prometheus scrape endpoint |
| `3000` | `3000` | TCP | grafana | Grafana dashboard |

---

## 3. End-to-End Ping Test to Google

### 3.1 Data Path Overview

```
  nr_ue container           nr_gnb container         UPF container           Internet
  ─────────────────         ─────────────────         ─────────────         ───────────
  uesimtun0                                           ogstun (tun)
  192.168.100.x                                       192.168.100.0/24
       │                                                    │
       │  ICMP Echo  →  GTP-U encap  →  UDP:2152  →  GTP-U decap  →  NAT  →  8.8.8.8
       │  (src: 192.168.100.x, dst: 8.8.8.8)
       ◄──────────────────────────────────────────────────────────────────────
          ICMP Reply ← GTP-U encap ← UDP:2152 ← GTP-U decap ← NAT ← 8.8.8.8
```

---

### 3.2 Pre-requisites Checklist

Before running the ping test, confirm the following:

1. **Core NFs are up**
   ```bash
   docker compose -f sa-deploy.yaml ps
   # All containers should show status: Up
   ```

2. **UE is registered and has a PDU session**
   ```bash
   docker logs nr_ue 2>&1 | grep -E "PDU Session Established|UE Address"
   # Expected: "PDU Session Established" and an assigned IP like 192.168.100.2
   ```

3. **UPF tun interface is created**
   ```bash
   docker exec upf ip addr show ogstun
   # Expected: inet 192.168.100.1/24
   ```

4. **IP forwarding is enabled on UPF**
   ```bash
   docker exec upf sysctl net.ipv4.ip_forward
   # Expected: net.ipv4.ip_forward = 1
   ```

5. **NAT masquerade rule is active on UPF**
   ```bash
   docker exec upf nft list ruleset | grep masquerade
   # or
   docker exec upf iptables -t nat -L POSTROUTING -n -v
   # Expected: MASQUERADE rule on ogstun towards external interface
   ```

---

### 3.3 Ping Test — From Inside the UE Container

```bash
# Step 1 — Exec into the nr_ue container
docker exec -it nr_ue bash

# Step 2 — Identify the UE tunnel interface (created after PDU session)
ip addr show uesimtun0
# Expected output:
#   inet 192.168.100.2/32 scope global uesimtun0

# Step 3 — Send ICMP ping to Google DNS via the UE tunnel interface
ping -I uesimtun0 8.8.8.8 -c 4

# Expected successful output:
# PING 8.8.8.8 (8.8.8.8) from 192.168.100.2 uesimtun0: 56(84) bytes of data.
# 64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=XX ms
# 64 bytes from 8.8.8.8: icmp_seq=2 ttl=116 time=XX ms
# 64 bytes from 8.8.8.8: icmp_seq=3 ttl=116 time=XX ms
# 64 bytes from 8.8.8.8: icmp_seq=4 ttl=116 time=XX ms
# --- 8.8.8.8 ping statistics ---
# 4 packets transmitted, 4 received, 0% packet loss
```

---

### 3.4 Ping Test — Using UERANSIM Built-in CLI

UERANSIM provides `nr-cli` to interact with the UE without entering the container:

```bash
# List active UE sessions
docker exec nr_ue nr-cli imsi-001011234567895 -e status

# Run ping via the UE's PDU session directly
docker exec nr_ue nr-cli imsi-001011234567895 -e "ps-list"

# Alternatively trigger ping from the UE process
docker exec nr_ue ping -I uesimtun0 8.8.8.8 -c 4
```

---

### 3.5 Verifying Each Hop Along the Path

```bash
# --- Hop 1: UE → gNB (Uu / radio sim) ---
# Check gNB sees the UE connected
docker logs nr_gnb 2>&1 | grep -E "UE.*connected|NGSetup"

# --- Hop 2: gNB → UPF (N3 GTP-U) ---
# Capture GTP-U traffic on UPF
docker exec upf tcpdump -i eth0 udp port 2152 -n -c 10

# --- Hop 3: UPF → Internet (NAT on ogstun) ---
# Capture traffic leaving ogstun
docker exec upf tcpdump -i ogstun icmp -n -c 10

# --- Hop 4: Verify DNS resolution also works through the tunnel ---
docker exec nr_ue nslookup google.com
# Uses SMF-assigned DNS: 8.8.8.8 (SMF_DNS1) / 8.8.4.4 (SMF_DNS2)
```

---

### 3.6 Troubleshooting Ping Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `uesimtun0: No such device` | PDU session not established | Check `docker logs nr_ue`; re-register UE |
| Ping from uesimtun0 times out | NAT not configured on UPF | Verify `iptables -t nat -L` inside UPF container |
| Ping reaches UPF but not Internet | IP forwarding disabled | `docker exec upf sysctl -w net.ipv4.ip_forward=1` |
| `Network unreachable` | No default route via uesimtun0 | `docker exec nr_ue ip route`; check PDU session type=IPv4 |
| N2 setup fails | AMF not reachable from gNB | Confirm AMF_IP=`172.22.0.10` in `.env` matches running AMF container |
| Authentication failure | IMSI/KI mismatch | Verify subscriber was added to MongoDB with correct credentials |

---

### 3.7 SMF DNS Configuration

The SMF pushes the following DNS servers to the UE during PDU session establishment:

| DNS Server | IP |
|------------|-----|
| Primary (SMF_DNS1) | `8.8.8.8` |
| Secondary (SMF_DNS2) | `8.8.4.4` |

These are injected into the UE's PDU session and accessible via the `uesimtun0` interface after a successful PDU session establishment.

---

## 4. Packet Capture — Docker Bridge (All Traffic from Host)

### Why the Docker Bridge Approach?

All containers in `docker_open5gs_default` communicate over a Linux bridge interface created on the **Docker host**. Every packet between any two containers — N2, N3, N4, SBI, radio simulation — crosses this bridge. A single `tcpdump` on the bridge interface from the **host** therefore captures the entire 5G network without `docker exec` into any container.

```
Docker Host (172.29.163.51)
│
├── br-<id>  ◄── THIS is what you capture on
│    ├── veth ── amf       (172.22.0.10)
│    ├── veth ── smf       (172.22.0.7)
│    ├── veth ── upf       (172.22.0.8)
│    ├── veth ── nr_gnb    (172.22.0.23)
│    ├── veth ── nr_ue     (172.22.0.24)
│    └── veth ── ...all other containers
```

All inter-container traffic (SCTP/NGAP, GTP-U, PFCP, SBI HTTP/2) flows through this single bridge.

> **Note:** GTP-U decapsulated traffic on `ogstun` (inside the UPF container) is NOT visible on the bridge — use Section 5.6 for that.

---

### 4.1 Identify the Docker Bridge Interface

```bash
# Find the bridge name for the docker_open5gs_default network
docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | cut -c1-12 | xargs -I{} echo "br-{}"

# Or list all bridges and match by subnet
ip -br link show type bridge

# Detailed — shows bridge name and attached interfaces
bridge link show

# One-liner to get the exact bridge interface name
BRIDGE=$(docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | head -c 12 | xargs -I{} echo "br-{}")
echo "Bridge interface: $BRIDGE"
```

Expected output example:
```
br-3f9a1c2e7d4b
```

---

### 4.2 Capture All 5G Traffic on the Bridge (Single Command)

```bash
# Set bridge variable (run once)
BRIDGE=$(docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | head -c 12 | xargs -I{} echo "br-{}")

# Capture EVERYTHING between all containers — full call flow
tcpdump -i $BRIDGE -w ./pcaps/all_5g_traffic.pcap

# With timestamps and no DNS resolution (cleaner output)
tcpdump -i $BRIDGE -tttt -n -w ./pcaps/all_5g_traffic.pcap
```

Open `all_5g_traffic.pcap` in Wireshark — it will contain N2, N3, N4, SBI, and radio simulation traffic all in one file.

---

### 4.3 Targeted Bridge Captures by Protocol

```bash
BRIDGE=$(docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | head -c 12 | xargs -I{} echo "br-{}")

# N2 — NGAP control plane (gNB ↔ AMF)
tcpdump -i $BRIDGE sctp -w ./pcaps/bridge_n2_ngap.pcap

# N3 — GTP-U user plane (gNB ↔ UPF)
tcpdump -i $BRIDGE udp port 2152 -w ./pcaps/bridge_n3_gtp.pcap

# N4 — PFCP session control (SMF ↔ UPF)
tcpdump -i $BRIDGE udp port 8805 -w ./pcaps/bridge_n4_pfcp.pcap

# SBI — All NF-to-NF HTTP/2 messages (:7777)
tcpdump -i $BRIDGE tcp port 7777 -w ./pcaps/bridge_sbi.pcap

# Radio simulation between gNB and UE
tcpdump -i $BRIDGE udp port 4997 -w ./pcaps/bridge_radio_sim.pcap

# All traffic to/from AMF only (172.22.0.10)
tcpdump -i $BRIDGE host 172.22.0.10 -w ./pcaps/bridge_amf_only.pcap

# All traffic to/from UPF only (172.22.0.8)
tcpdump -i $BRIDGE host 172.22.0.8 -w ./pcaps/bridge_upf_only.pcap
```

---

### 4.4 Full End-to-End Parallel Bridge Capture

Capture the complete registration + PDU session + ping flow with a single background process:

```bash
BRIDGE=$(docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | head -c 12 | xargs -I{} echo "br-{}")

mkdir -p ./pcaps

# Start background capture on the bridge
tcpdump -i $BRIDGE -w ./pcaps/full_e2e_bridge.pcap &
TCPDUMP_PID=$!
echo "tcpdump started (PID $TCPDUMP_PID)"

# --- Run the test ---
docker compose -f nr-gnb.yaml up -d
sleep 5
docker compose -f nr-ue.yaml up -d
sleep 10
docker exec nr_ue ping -I uesimtun0 8.8.8.8 -c 4

# Stop capture
kill $TCPDUMP_PID
echo "Capture saved to ./pcaps/full_e2e_bridge.pcap"

# Open in Wireshark
wireshark ./pcaps/full_e2e_bridge.pcap
```

---

### 4.5 What You Will See in the Bridge Capture

| Time | Packet | Wireshark Filter |
|------|--------|-----------------|
| t=0s | gNB → AMF: NG Setup Request | `ngap` |
| t=0s | AMF → gNB: NG Setup Response | `ngap` |
| t=1s | UE → AMF: Registration Request (via gNB N2) | `ngap` |
| t=1s | AMF → AUSF: Nausf_UEAuthentication (HTTP/2) | `http2` |
| t=1s | AMF → UDM: Nudm_SDM_Get (HTTP/2) | `http2` |
| t=2s | UE ↔ AMF: NAS Authentication exchange | `ngap` |
| t=3s | AMF → SMF: Nsmf_PDUSession_Create (HTTP/2) | `http2` |
| t=3s | SMF → UPF: PFCP Session Establishment | `pfcp` |
| t=4s | AMF → gNB: PDU Session Resource Setup | `ngap` |
| t=4s | GTP-U tunnel active (gNB ↔ UPF) | `gtp` |
| t=10s | ICMP Echo inside GTP-U tunnel | `gtp and icmp` |

---

### 4.6 Live View on Terminal (No File)

For quick real-time inspection without saving a file:

```bash
BRIDGE=$(docker network inspect docker_open5gs_default \
  --format '{{.Id}}' | head -c 12 | xargs -I{} echo "br-{}")

# Live print of all NGAP messages
tcpdump -i $BRIDGE -n sctp

# Live print of GTP-U packets with inner IP header
tcpdump -i $BRIDGE -n -v udp port 2152

# Live print of PFCP messages
tcpdump -i $BRIDGE -n -v udp port 8805

# Live print of SBI HTTP/2 (shows TCP segments — use Wireshark for full decode)
tcpdump -i $BRIDGE -n -A tcp port 7777 | grep -E "POST|GET|HTTP|nsmf|namf|nudm|nausf|nnrf"
```

---

### 4.7 Bridge Capture Limitations

| Limitation | Details |
|------------|---------|
| `ogstun` traffic not visible | GTP-U decapsulated user traffic lives inside the UPF container's tun interface. Use `docker exec upf tcpdump -i ogstun` for this (Section 5.6) |
| Host ↔ container traffic | Only inter-container traffic is on the bridge. Host-initiated connections use `veth` pairs directly |
| GTP-U inner IP | Wireshark decodes the inner IP inside GTP-U automatically — apply filter `ip.src == 192.168.100.0/24` to see UE traffic |
| Requires root on host | `tcpdump` on the bridge interface requires `sudo` or root on the Docker host |

---

## 5. Packet Capture — Per-Interface Inside Containers

### 5.1 Interface-to-Capture Map

| Interface | Container | Capture Interface | Traffic Type |
|-----------|-----------|-------------------|--------------|
| N2 (NGAP) | amf / nr_gnb | `eth0` | SCTP :38412 — control plane |
| N3 (GTP-U) | upf / nr_gnb | `eth0` | UDP :2152 — user plane |
| N4 (PFCP) | smf / upf | `eth0` | UDP :8805 — session rules |
| SBI (HTTP/2) | amf, smf, ausf, udm, udr, pcf, nrf, scp | `eth0` | TCP :7777 |
| UE tun | upf | `ogstun` | ICMP / data after GTP-U decap |
| Radio Sim | nr_gnb / nr_ue | `eth0` | UDP :4997 |

---

### 5.2 Capture N2 (NGAP) — UE Registration & Session Setup

Captures all NGAP messages between the gNB and AMF (NG Setup, Initial UE Message, PDU Session Resource Setup, etc.):

```bash
# On the AMF container — capture inbound SCTP from gNB
docker exec amf tcpdump -i eth0 sctp -w /tmp/n2_amf.pcap

# On the gNB container — capture outbound SCTP to AMF
docker exec nr_gnb tcpdump -i eth0 sctp -w /tmp/n2_gnb.pcap

# Copy pcap to host for Wireshark analysis
docker cp amf:/tmp/n2_amf.pcap ./n2_amf.pcap
docker cp nr_gnb:/tmp/n2_gnb.pcap ./n2_gnb.pcap
```

> **Wireshark dissector:** Wireshark auto-dissects NGAP over SCTP port 38412. Apply filter: `ngap` or `sctp.port == 38412`.

---

### 5.3 Capture N3 (GTP-U) — User Plane Tunnel

Captures the GTP-U encapsulated user data between the gNB and UPF:

```bash
# On the UPF container — all GTP-U traffic
docker exec upf tcpdump -i eth0 udp port 2152 -w /tmp/n3_upf.pcap

# On the gNB container
docker exec nr_gnb tcpdump -i eth0 udp port 2152 -w /tmp/n3_gnb.pcap

# Copy to host
docker cp upf:/tmp/n3_upf.pcap ./n3_upf.pcap
```

> **Wireshark dissector:** Apply filter `gtp` to decode the GTP-U header and inner IP packets. Use `gtp and icmp` to isolate ping packets inside the tunnel.

---

### 5.4 Capture N4 (PFCP) — Session Management Between SMF and UPF

Captures PFCP Session Establishment, Modification, and Deletion messages:

```bash
# On the UPF container
docker exec upf tcpdump -i eth0 udp port 8805 -w /tmp/n4_upf.pcap

# On the SMF container
docker exec smf tcpdump -i eth0 udp port 8805 -w /tmp/n4_smf.pcap

# Copy to host
docker cp upf:/tmp/n4_upf.pcap ./n4_upf.pcap
docker cp smf:/tmp/n4_smf.pcap ./n4_smf.pcap
```

> **Wireshark dissector:** Apply filter `pfcp` to view all PFCP messages. Key messages: `PFCP Session Establishment Request/Response`, `PFCP Session Modification Request/Response`.

---

### 5.5 Capture SBI (HTTP/2) — Control Plane NF-to-NF Messages

Captures all Service-Based Interface messages (registration, authentication, policy, session) between 5GC network functions:

```bash
# Capture all SBI traffic on the AMF (N11, N12, N15, Nnrf)
docker exec amf tcpdump -i eth0 tcp port 7777 -w /tmp/sbi_amf.pcap

# Capture NRF registration traffic
docker exec nrf tcpdump -i eth0 tcp port 7777 -w /tmp/sbi_nrf.pcap

# Capture AUSF authentication traffic
docker exec ausf tcpdump -i eth0 tcp port 7777 -w /tmp/sbi_ausf.pcap

# Capture SMF session management (N7, N10, N11)
docker exec smf tcpdump -i eth0 tcp port 7777 -w /tmp/sbi_smf.pcap

# Copy all to host
for nf in amf nrf ausf smf udm udr pcf; do
  docker cp ${nf}:/tmp/sbi_${nf}.pcap ./sbi_${nf}.pcap 2>/dev/null || true
done
```

> **Wireshark dissector:** Apply filter `http2` to decode 5GC REST/JSON messages. Use `http2.header.value contains "namf"` to filter AMF service calls.

---

### 5.6 Capture Decapsulated User Plane — Post-GTP on ogstun

Captures plain IP packets (e.g., ICMP to 8.8.8.8) after GTP-U has been stripped on the UPF tun interface:

```bash
# Capture ICMP on the UPF tun interface (decapsulated user traffic)
docker exec upf tcpdump -i ogstun icmp -w /tmp/user_plane_icmp.pcap

# Capture all IP traffic through the UE internet APN tunnel
docker exec upf tcpdump -i ogstun -w /tmp/user_plane_all.pcap

# Copy to host
docker cp upf:/tmp/user_plane_icmp.pcap ./user_plane_icmp.pcap
docker cp upf:/tmp/user_plane_all.pcap ./user_plane_all.pcap
```

> **Wireshark filter:** `icmp and ip.addr == 8.8.8.8` to isolate ping packets.

---

### 5.7 Full End-to-End Capture — All Interfaces Simultaneously

Use this to capture a complete 5G call flow (registration + PDU session + ping) in parallel:

```bash
# Start captures on all key interfaces in background
docker exec -d amf    tcpdump -i eth0 -w /tmp/cap_amf.pcap
docker exec -d nr_gnb tcpdump -i eth0 -w /tmp/cap_gnb.pcap
docker exec -d upf    tcpdump -i eth0 -w /tmp/cap_upf_n3.pcap
docker exec -d upf    tcpdump -i ogstun -w /tmp/cap_upf_tun.pcap
docker exec -d smf    tcpdump -i eth0 -w /tmp/cap_smf.pcap

# --- Run your test (e.g., start UE and ping) ---
docker compose -f nr-ue.yaml up -d
sleep 10
docker exec nr_ue ping -I uesimtun0 8.8.8.8 -c 4

# Stop tcpdump in each container
for c in amf nr_gnb upf smf; do
  docker exec $c pkill tcpdump 2>/dev/null || true
done

# Collect all pcaps to host ./pcaps/ directory
mkdir -p ./pcaps
docker cp amf:/tmp/cap_amf.pcap         ./pcaps/cap_amf.pcap
docker cp nr_gnb:/tmp/cap_gnb.pcap      ./pcaps/cap_gnb.pcap
docker cp upf:/tmp/cap_upf_n3.pcap      ./pcaps/cap_upf_n3.pcap
docker cp upf:/tmp/cap_upf_tun.pcap     ./pcaps/cap_upf_tun.pcap
docker cp smf:/tmp/cap_smf.pcap         ./pcaps/cap_smf.pcap
```

---

### 5.8 Wireshark Filter Reference

| Scenario | Wireshark Display Filter |
|----------|--------------------------|
| All NGAP messages | `ngap` |
| UE registration only | `ngap.procedureCode == 14` |
| GTP-U user plane | `gtp` |
| Ping inside GTP tunnel | `gtp and icmp` |
| PFCP session control | `pfcp` |
| SBI HTTP/2 all | `http2` |
| AMF service operations | `http2.header.value contains "namf"` |
| SMF service operations | `http2.header.value contains "nsmf"` |
| UDM service operations | `http2.header.value contains "nudm"` |
| AUSF authentication | `http2.header.value contains "nausf"` |
| NRF registration | `http2.header.value contains "nnrf"` |
| Plain ICMP (after NAT) | `icmp and ip.addr == 8.8.8.8` |
| SCTP only | `sctp` |

---

### 5.9 Merge and Analyse All Captures with mergecap

To merge all pcap files into a single chronological file for full end-to-end analysis:

```bash
# Install mergecap (part of Wireshark tools)
sudo apt-get install -y wireshark-common

# Merge all pcaps sorted by timestamp
mergecap -w ./pcaps/full_capture.pcap ./pcaps/*.pcap

# Optional: convert to pcapng with interface labels
mergecap -F pcapng -w ./pcaps/full_capture.pcapng ./pcaps/*.pcap

# Open in Wireshark
wireshark ./pcaps/full_capture.pcapng
```

---

*Report generated for Open5GS + UERANSIM deployment on Docker network `172.22.0.0/24`, PLMN 001-01.*
