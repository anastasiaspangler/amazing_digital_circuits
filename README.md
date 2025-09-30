# Amazing Digital Circuits ⚡

**Realtime control + on-the-fly reprogramming + prop generation = pure magic**
<img width="1826" height="958" alt="original" src="https://github.com/user-attachments/assets/1654b05c-7c1e-47d5-acbc-d3783e43ae84" />

## 🎯 What it is

“Amazing Digital Circuits” is a system that allows you to:

- **Reprogram a control board in *natural language*** (i.e. talk to it, it listens, it acts)
- **Generate props / artifacts** in realtime using Blender & AI tooling
- **Pipeline everything together** so it all plays live / interactively

---

## 🚀 Why I built it

This project explores:

- Combining **hardware + software + AI** in one interactive system  
- **Orchestrating real-time flows** instead of just static code  
- Tackling problems where things break, timing matters, and multiple domains collide  

---

## 🧩 Architecture (high level)

| Component | Role |
|-----------|------|
| **Language interface** | Accepts natural language commands (“do X”, “change Y”) |
| **Control board module** | Takes commands, programs/tweaks hardware parameters in realtime |
| **Blender / props engine** | Generates visual or physical props based on instructions |
| **Orchestrator / glue** | Ensures smooth, low-latency interplay among modules |

---

## 🛠️ Tech stack & key challenges

- **Languages & tools**: Python, Blender scripting, possibly embedded C/C++ for control board  
- **Realtime / latency**: minimizing lag between “command input” → “hardware response / prop output”  
- **Error handling & safety**: fallback modes, sanity checks on commands  
- **Scalable design**: modular so new hardware or effect modules can be swapped in  

---

## 🎯 Demo / Proof

1. Spin up `app.py` / `main.py` locally  
2. Send a natural language command like “Change voltage on channel A to 5 V”  
3. Watch the prop get adjusted / regenerated in Blender or the hardware respond  

---

## 📂 How to use

1. Clone the repo  
2. Install dependencies (`pip install -r requirements.txt`)  
3. Hook up the control board (if hardware is available)  
4. Run `main.py` (or `app.py`)  
5. Send a command, watch it dance  
