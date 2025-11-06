# 🕒 NikKos Clock — Raspberry Pi Pico W

### Internet-Synchronized LED Clock  
A Wi-Fi enabled **digital clock and message display**, built on a **Raspberry Pi Pico W** with a **MAX7219 4-in-1 LED matrix**.

---

## ✨ Features

✅ Real-time synchronization via NTP (Europe/Athens timezone)  
✅ Automatic Daylight Saving Time (DST) adjustment  
✅ Web interface for control (no external buttons required)  
✅ Show date and scroll custom messages via browser  
✅ Smooth blinking colon effect on the LED display  
✅ Adaptive brightness (day / evening / night)  
✅ UTF-8 safe / mobile-friendly web UI  
✅ Lightweight MicroPython code (compatible with v1.21 – v1.26)

---

## 🧰 Hardware Required

| Component | Description |
|------------|-------------|
| **Raspberry Pi Pico W** | Main controller (dual-core Wi-Fi microcontroller) |
| **MAX7219 4-in-1 LED Matrix** | 4 modules (32×8 pixels total) for clock display |
| **Wires + breadboard or PCB** | For SPI connections and power (3.3 V logic) |
| **Micro-USB cable** | For power and flashing the firmware |

---

## ⚡ Wiring Diagram (SPI Connection)

| MAX7219 Pin | Pico W Pin | Function |
|-------------:|-----------:|-----------|
| **VCC** | 3V3 (OUT) | Power |
| **GND** | GND | Ground |
| **DIN** | GP11 | MOSI |
| **CLK** | GP10 | SCK |
| **CS** | GP13 | Chip Select |

```
Pico W
 ┌──────────────┐
 │ [3V3]──►VCC  │
 │ [GND]──►GND  │
 │ [GP11]─►DIN  │
 │ [GP10]─►CLK  │
 │ [GP13]─►CS   │
 └──────────────┘
       │
   MAX7219 (4-in-1)
```

---

## 🧩 Project Structure

```
/flash/
├── main.py          # Main program (Web + Clock logic)
├── max7219.py       # MAX7219 driver library
└── wifi.json        # Wi-Fi credentials (JSON format)
```

#### Example `wifi.json`
```json
{
  "ssid": "YourWiFiName",
  "password": "YourPassword"
}
```

---

## 🌐 Web Interface Preview

When the Pico W connects successfully, it prints:

```
🌐 Web UI at: 192.168.X.X
```

Then open that IP in a browser (desktop or mobile):

| Function | Description |
|-----------|-------------|
| **🕒 Main page** | Displays current time and date |
| **📅 Show Date** | Scrolls the date on the LED matrix |
| **💬 Show Message** | Sends custom text to scroll on the display |

---

## 💻 Code Overview

(See `main.py` in this repository for full annotated source code.)

---

## 📸 Screenshot Examples (extras)

- 🕒 Main web page view  
- 💬 Custom message display on matrix  
- ⚙️ Device setup or 3D-printed enclosure  

---

## ⚙️ Build & Flash Instructions

1. Flash the latest **MicroPython for Raspberry Pi Pico W**  
2. Copy `main.py`, `max7219.py`, and `wifi.json` to the board  
3. Reset the Pico W  
4. Observe serial console (Wi-Fi + time sync logs)  
5. Open the printed IP in your browser → **Enjoy!**

---

## 🧠 Author & Credits
**Project by NikKos**  
Developed with 💡 MicroPython + Raspberry Pi Pico W
