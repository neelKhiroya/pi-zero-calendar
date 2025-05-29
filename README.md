# 📅 Pi Terminal Calendar Dashboard

A lightweight terminal-based dashboard for the Raspberry Pi Zero that displays:

- 📆 **Google Calendar** events
- ✅ **Google Tasks**
- 💻 **System info** (CPU, RAM, Temperature)

Built using Python and [Rich](https://github.com/Textualize/rich) for beautiful terminal rendering. No desktop environment required!

---

## 🔧 Features

- Authenticates with Google Calendar and Tasks API
- Rotating pages: **Today**, **Upcoming**, and **System Info**
- Smart event formatting:
  - Today: `3:30 PM`
  - This week: `Tue`
  - Later: `Jun 10`
- Compact and responsive layout using `rich.live`
- Designed for Raspberry Pi Zero but runs on any system with Python

---

## 🖥️ Preview
![IMG_4348](https://github.com/user-attachments/assets/0c557786-77d2-4460-aa16-fa2ab6082155)
![IMG_4350](https://github.com/user-attachments/assets/1d9873ec-a422-4d82-b3d6-d013e477a574)
![IMG_4351](https://github.com/user-attachments/assets/0864651b-a7ae-4d2c-a5ae-e90debf821fb)
![IMG_4347](https://github.com/user-attachments/assets/8ad383ba-309f-45eb-a926-68fb21885649)
![IMG_4307](https://github.com/user-attachments/assets/99547b99-f42c-42a4-a752-53b883685c2e)

---

## 🚀 Getting Started

### 1. Clone this repo

```bash
git clone https://github.com/yourusername/pi-terminal-dashboard.git
cd pi-terminal-dashboard
```
### 2. Create python environment & Install packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a Google Cloud Project
1. Go to [Goole Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable both **Google Calendar** and **Google Tasks API**
  - App type - Desktop
  - Download the client-secret(...).json and move it to the root of the repo
  - Add your email to the test user via the **Audience** tab.

### 4. Run the app
```bash
python calendar.py
```
You will be prompted to authorize the application in a new window. token.json will be saved for future session use.

### Notes
- You may need to authorize the app on a seperate computer and tranfer the token as a headless device cannot open a browser.
- You may want to install some python packages via the ubuntu repo, (apt) as some packages are too large to install via pip (pillow, numpy, etc...).

### TODO
- Fix screen flickering
- Add the option to scan a qr code from the rasberry pi to authenticate.
