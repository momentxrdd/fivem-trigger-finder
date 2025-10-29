# FiveM Trigger Finder  

A desktop app that scans your FiveM server and lists all triggers (events) with filtering options.  

## Features  
- 🔍 **Folder Selection** – Choose your FiveM server directory  
- 📂 **Auto Scan** – Scans all `.lua` and `.js` files  
- 🎯 **Trigger Detection** – Finds:  
  - TriggerEvent  
  - TriggerServerEvent  
  - RegisterNetEvent  
  - AddEventHandler  
  - RegisterServerEvent  
  - RegisterCommand  
  - ESX & QBCore Callbacks  
- 🔎 **Advanced Search** – Filter by name, path, or type  
- ⭐ **Custom Keywords** – Highlight triggers with predefined keywords  
- 📊 **Detailed Info** – Shows file path, line number, and trigger type  

## Setup  
### Requirements  
- Python 3.7+ (with tkinter)  

### Usage  
```bash
python trigger_finder.py
```

1. Click **Select Folder** and choose your FiveM server directory  
2. Click **Scan Triggers**  
3. Results will appear in the table  

## Custom Keywords  
On first launch, a `special_keywords.json` file is created. Edit it to add your own keywords.  

**Default keywords:**  
weapon, item, money, bank, admin, police, ems, mechanic, inventory, vehicle, drug, job, gang, blackmoney, society  

## Screenshot  
Displays:  
- Trigger name  
- File path  
- Line number  
- Trigger type (Client Event, Server Event, Command, etc.)  

## Notes  
- Supports UTF-8 encoding  
- Scanning may take a few seconds for large servers  
- Recursively scans all `.lua` and `.js` files
