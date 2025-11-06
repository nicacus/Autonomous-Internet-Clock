"""
NikKos Clock — Raspberry Pi Pico W
----------------------------------
Web + Custom Message Edition (stable, redirect enabled)
✓ NTP + DST (Europe/Athens)
✓ Continuous time refresh
✓ Blinking colon effect
✓ Web-only controls (Show Date + Custom Message)
✓ UTF-8 safe / responsive UI
✓ Requests redirect to main URL (/)
"""

import network, socket, ntptime, utime, json, ure
from machine import Pin, SPI
from max7219 import Matrix8x8

CONFIG_FILE = "wifi.json"
SYNC_INTERVAL = 43200  # 12 hours = 12 × 3600 s

# --------------------------------------------------
# Hardware Setup
# --------------------------------------------------
spi = SPI(1, baudrate=10_000_000, polarity=0, phase=0,
          sck=Pin(10), mosi=Pin(11))   # SPI pins for MAX7219
cs = Pin(13, Pin.OUT)
display = Matrix8x8(spi, cs, 4)        # 4 modules = 32×8 LEDs
display.brightness(5)

# --------------------------------------------------
# Wi-Fi Management
# --------------------------------------------------
def load_config():
    """Read Wi-Fi credentials from JSON file."""
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return None

def connect_wifi():
    """Connect to Wi-Fi using stored credentials."""
    cfg = load_config()
    if not cfg:
        print("⚠️ No Wi-Fi config found (wifi.json)")
        return None
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(cfg["ssid"], cfg["password"])
    print("🔗 Connecting to", cfg["ssid"])
    for _ in range(20):
        if wlan.isconnected():
            print("✅ Connected:", wlan.ifconfig())
            return wlan
        utime.sleep(1)
    print("❌ Could not connect.")
    return None

# --------------------------------------------------
# Time + DST Handling
# --------------------------------------------------
def sync_time(retries=3, delay=2):
    """Synchronize time from NTP server."""
    global last_sync
    ntptime.host = "gr.pool.ntp.org"
    for i in range(retries):
        try:
            ntptime.settime()
            last_sync = utime.time()
            print(f"✅ Time synced (attempt {i+1})")
            return True
        except Exception as e:
            print("⚠️ NTP failed:", e)
            utime.sleep(delay)
    print("⚠️ Keeping previous time")
    return False

def localtime_athens():
    """Return local time for Athens (GR) with DST."""
    t = utime.localtime(utime.time())
    y, m, d = t[0:3]
    def last_sunday(mon):
        for day in range(31, 24, -1):
            try:
                if utime.localtime(utime.mktime((y, mon, day, 0,0,0,0,0)))[6] == 6:
                    return day
            except: pass
        return 31
    start, end = last_sunday(3), last_sunday(10)
    offset = 3 if (m>3 and m<10) or (m==3 and d>=start) or (m==10 and d<end) else 2
    return utime.localtime(utime.time() + offset*3600)

# --------------------------------------------------
# LED Display
# --------------------------------------------------
def scroll_text(txt, speed=0.04):
    """Scroll text smoothly across the matrix."""
    for i in range(len(txt)*8 + 32):
        display.fill(0)
        display.text(txt, 32 - i, 0, 1)
        display.show()
        utime.sleep(speed)

def adjust_brightness(h):
    """Adjust brightness based on hour of day."""
    if 7 <= h < 19:
        display.brightness(7)
    elif 19 <= h < 22:
        display.brightness(4)
    else:
        display.brightness(2)

# --------------------------------------------------
# Web Interface HTML
# --------------------------------------------------
def web_page(time_str, date_str):
    """Generate HTML page shown in browser."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        "<title>NikKos Clock</title></head>"
        "<body style='text-align:center;font-family:Arial;margin-top:60px;'>"
        f"<h1 style='font-size:52px;'>{time_str}</h1>"
        f"<h2 style='color:#007BFF;'>{date_str}</h2>"
        "<form action='/show_date'>"
        "<button style='font-size:24px;padding:10px 20px;'>📅 Show Date</button>"
        "</form><br>"
        "<form action='/msg' method='GET'>"
        "<input name='text' placeholder='Enter message...' "
        "style='font-size:20px;width:70%;padding:5px;text-align:center;'><br><br>"
        "<button style='font-size:22px;padding:8px 16px;'>Show Message</button>"
        "</form>"
        "</body></html>"
    )

# --------------------------------------------------
# Boot Sequence
# --------------------------------------------------
wlan = connect_wifi()
if wlan:
    sync_time()
else:
    print("⚠️ Offline mode")

last_sync = utime.time()
scroll_text("HELLO")

# Initialize web server socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(1)
s.settimeout(0.05)

if wlan:
    print("🌐 Web UI at:", wlan.ifconfig()[0])

blink = True
blink_timer = utime.ticks_ms()

# --------------------------------------------------
# Main Loop
# --------------------------------------------------
while True:
    if wlan and (utime.time() - last_sync > SYNC_INTERVAL):
        sync_time()

    if utime.ticks_diff(utime.ticks_ms(), blink_timer) > 500:
        blink = not blink
        blink_timer = utime.ticks_ms()

    t = localtime_athens()
    adjust_brightness(t[3])
    hora = "{:02d}{:02d}".format(t[3], t[4])
    horaweb = "{:02d}:{:02d}".format(t[3], t[4])


    display.fill(0)
    display.text(hora, 0, 0, 1)
    if blink:
        display.pixel(15, 7, 1)
    display.show()

    try:
        cl, _ = s.accept()
        req = cl.recv(1024).decode()

        # Handle custom message
        if "GET /msg?text=" in req:
            match = ure.search(r"/msg\?text=([^& ]+)", req)
            if match:
                msg = match.group(1).replace("+", " ").replace("%20", " ")
                scroll_text(msg)
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue

        # Handle date button
        elif "GET /show_date" in req:
            scroll_text("{:02d}/{:02d}/{:04d}".format(t[2], t[1], t[0]))
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue

        # Serve main page
        date_str = "{:02d}/{:02d}/{:04d}".format(t[2], t[1], t[0])
        html = web_page(horaweb, date_str)
        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html)}\r\n"
            "Connection: close\r\n\r\n"
        )
        cl.sendall(header + html)
        cl.close()

    except OSError:
        pass

    utime.sleep_ms(50)