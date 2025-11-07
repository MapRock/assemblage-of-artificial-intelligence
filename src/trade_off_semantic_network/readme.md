# 🦕 Soft-Coded Logic – Prolog in the LLM Era  
### AI "Go-to-Market" 3rd Anniversary Special – TOSN Demonstration

This repository accompanies the blog **“Soft-Coded Logic – Prolog in the LLM Era”**,  
part of my ongoing *Prolog in the LLM Era* series.  
It introduces the **Trade-Off Semantic Network (TOSN)** — a hybrid graph that connects **knowledge graphs (SN)** and **causal trade-off models (TO)**.  
Together, they demonstrate how a knowledge graph can serve as the **model of what can exist**,  
while **Prolog rules** dynamically score relationships according to context.

---

## 🧩 Concept Overview

| Layer | Role | Description |
|-------|------|--------------|
| **SN – Semantic Network** | *Structure* | Represents entities such as SQL Server, its components, computer hardware, and operating systems. Think of it as the *ontology of things*. |
| **TO – Trade-Off Graph** | *Causality* | Represents directional cause-and-effect relationships between metrics and configuration settings. |
| **Prolog Layer** | *Confidence Scoring* | Evaluates the strength (0–1) of edges dynamically, based on real-time context (performance, configuration, workload). |
| **Temporal Map** | *Observation* | Captures the time evolution of node states — not manually edited, but generated from event streams. |

Together they form the **TOSN**, a structure that’s both *descriptive* (SN) and *prescriptive* (TO).

---

## 📂 Repository Contents

| File | Description |
|------|--------------|
| **ontology.ttl** | The *Semantic Network (SN)* — defines classes and relationships for SQL Server, its components, and underlying hardware. |
| **metrics.ttl** | Defines performance counters from Windows and SQL Server (and a few abstracted Profiler metrics). |
| **config.ttl** | Configuration settings that can be tuned, with links (`to:affects`) to metrics they influence. |
| **tosn-links.ttl** | The *Trade-Off (TO)* layer — causal relationships between metrics, representing “elemental” chains like `PLE → Page Faults/sec → Disk Latency → Query Latency`. |

All four together can be loaded into **Protégé** to visualize and query the TOSN.

---

## 🦾 How to Load the TOSN in Protégé

### 1. Install Protégé
- Download from [https://protege.stanford.edu](https://protege.stanford.edu)
- Open Protégé (desktop edition is fine).

### 2. Create a New Project
- Go to **File → New Project → OWL RDF/XML** (or **Turtle**, if available).
- Save the project (e.g., `TOSN-Project.pprj`).

### 3. Import the TTL Files
Each TTL file is modular, so you’ll import them into a single ontology window:

1. Open your new project.  
2. Go to **Refactor → Import Ontology → From a Local File...**  
3. Import these **four** in this order (to keep namespace context tidy):
   1. `ontology.ttl`
   2. `metrics.ttl`
   3. `config.ttl`
   4. `tosn-links.ttl`

4. When prompted, choose **“Import as separate ontology (keep their IRIs)”**.

> 💡 *Tip:* Protégé shows the imported ontologies in the **Active Ontologies** tab.  
> If you prefer one unified file, you can merge them later via **File → Export → RDF/XML or Turtle**.

---

## 🔍 Navigating the Ontology

Once loaded:

- **Classes tab:** explore `sn:SoftwareProduct`, `sn:SoftwareComponent`, and `mt:Metric`.  
- **Object Properties:** look for  
  - `sn:hasComponent`  
  - `to:affects` (config → metric)  
  - `to:influences` (metric → metric).  
- **Individuals tab:** check the example instance `ex:SQLInstanceA` and follow its connections to metrics and configs.  
- **Graph view (OntoGraf plug-in):** visualize `to:influences` chains — the **TO layer**.  
  - Example chain:  
    `PLE ↓ → PageFaults/sec ↓ → Disk_ReadLatency ↓ → IOWaitPct ↓ → QueryLatencyMs ↓`

---

## 🧠 How This Fits the Blog

In the blog post, this ontology represents the **“soft-coded logic”** idea:

- The **knowledge graph (SN)** defines *what exists*.  
- The **Prolog rules** define *how strong those relationships are under specific conditions*.  
- The **TOSN** bridges the two — connecting *knowledge* to *action*.

By expressing SQL Server performance and configuration as a causal graph, we can model how settings, metrics, and hardware characteristics interact — just like a living system with feedback loops.

---

## 🪐 License and Attribution
This sample ontology is provided for educational and demonstration purposes.  
Feel free to fork and adapt it for your own enterprise or academic work.  
When referencing or reusing, please credit:

**© 2025 Eugene Asahara**  
*“Soft-Coded Logic – Prolog in the LLM Era”*  
[https://eugeneasahara.com](https://eugeneasahara.com)

---

## 💡 Next Steps
Future iterations may include:
- Temporal event snapshots as RDF (`Observation` class).  
- Integration with a simple Prolog inference layer (e.g., SWI-Prolog or Tau Prolog via JSON-LD).  
- Visualization of edge strength over time (as a “context heatmap”).  

---

> 🦕 *“Prolog may be prehistoric, but in this series it finally gets to headline again.”*

