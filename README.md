# **Amazing Digital Circuits**

## Overview
<img width="1826" height="958" alt="original" src="https://github.com/user-attachments/assets/1654b05c-7c1e-47d5-acbc-d3783e43ae84" />
This project demonstrates a local, open-source pipeline for controlling Blender through natural language.  
A lightweight model (**gpt-oss:20b**) interprets text commands and executes corresponding Python functions inside Blender via a Flask bridge.  
The system enables full-scene manipulation and simple animation without directly using the Blender interface.

---

## System Description

### Core Components

| Component | Function |
|------------|-----------|
| **gpt-oss:20b** | Local open-source model served through Ollama. Maps natural language to Blender tool calls. |
| **Flask server** | Handles remote procedure calls between the language model and Blender’s scripting API. |
| **Blender scripting** | Executes generated Python functions (e.g., transformations, animations, object creation). |
| **Optional physical controls** | Buttons mapped to stored tool calls for real-time, repeatable actions. |

## How to Run it
1. Have ollama serving in the background
2. Copy and paste the blender code into the scripting tab of Blender a run.
3. Set Replicate env. variable if you want to make props
4. Run the Flask app
5. Open the chat

## Helpful Links
I have a Repo just on remote control for Blender: https://github.com/anastasiaspangler/remote_blender

Gpt-oss:20B Model Card: https://ollama.com/library/gpt-oss:20b

Replicate Model Used for 3D Generation: https://replicate.com/firtoz/trellis

