import os
import sys
import time
import random
import asyncio
import logging
import datetime
import threading
import requests

from pyrogram import Client, filters
from pyrogram.types import Message
from telethon import TelegramClient, events

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from queue import Queue

# ======================= CONFIGURATION ==========================
API_ID = 24235215
API_HASH = "f344f64fc2e54099684b09273a4d445b"
BOT_TOKEN = "7566331132:AAHVsipJXKijZHBk1tXvtiMPZqc7ll-OHTA"

PROXY_LIST_FILE = "proxies.txt"
USER_AGENT_LIST = [
    # A handful of modern UA strings for humanization
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Mobile Safari/537.36"
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ======================= PROXY MANAGER ==========================
class ProxyManager:
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.Lock()
        self.proxies = self._load_proxies()

    def _load_proxies(self):
        logging.info("Loading proxies...")
        proxies = []
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        proxies.append(line)
        logging.info(f"{len(proxies)} proxies loaded.")
        return proxies

    def get_random_proxy(self):
        with self.lock:
            if not self.proxies:
                return None
            return random.choice(self.proxies)

    def reload(self):
        with self.lock:
            self.proxies = self._load_proxies()

    def get_count(self):
        with self.lock:
            return len(self.proxies)

proxy_manager = ProxyManager(PROXY_LIST_FILE)

# ======================= USER AGENT MANAGER =====================
def get_random_user_agent():
    return random.choice(USER_AGENT_LIST)

# ======================= BROWSER AUTOMATION =====================
class HumanLikeBrowser:
    def __init__(self, url, proxy=None, headless=True, timeout=40):
        self.url = url
        self.proxy = proxy
        self.headless = headless
        self.timeout = timeout
        self.driver = None

    def _get_chrome_options(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"user-agent={get_random_user_agent()}")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size={0},{1}".format(
            random.randint(1050, 1920), random.randint(700, 1280)
        ))
        if self.headless:
            options.add_argument("--headless=new")
        # Proxy support
        if self.proxy:
            if self.proxy.startswith("socks"):
                options.add_argument(f"--proxy-server={self.proxy}")
            else:
                options.add_argument(f"--proxy-server=http://{self.proxy}")
        return options

    def _init_driver(self):
        # ChromeDriver must be in PATH for Termux (can use chromium package)
        try:
            options = self._get_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            logging.error(f"Failed to initialize webdriver: {e}")
            raise

    def _simulate_human_behavior(self):
        driver = self.driver
        actions = ActionChains(driver)
        width = driver.get_window_size()['width']
        height = driver.get_window_size()['height']
        # Mouse movement: random patterns
        for _ in range(random.randint(4, 10)):
            x = random.randint(0, width - 20)
            y = random.randint(0, height - 20)
            try:
                actions.move_by_offset(x, y).perform()
            except Exception:
                pass
            time.sleep(random.uniform(0.2, 0.9))
        # Random scrolls
        for _ in range(random.randint(2, 5)):
            scroll_amount = random.randint(50, height)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 1.1))
        driver.execute_script("window.scrollTo(0, 0);")
        # Click random elements
        all_elems = driver.find_elements(By.XPATH, "//*")
        random.shuffle(all_elems)
        clicked = 0
        for elem in all_elems:
            if clicked >= random.randint(1, 4):
                break
            try:
                actions.move_to_element(elem).click().perform()
                clicked += 1
                time.sleep(random.uniform(0.2, 0.6))
            except Exception:
                continue
        # Random keyboard input (no submit)
        body = None
        try:
            body = driver.find_element(By.TAG_NAME, "body")
        except Exception:
            pass
        if body:
            for _ in range(random.randint(1, 3)):
                key = random.choice([Keys.ARROW_DOWN, Keys.ARROW_RIGHT, Keys.ARROW_LEFT, Keys.ARROW_UP])
                body.send_keys(key)
                time.sleep(random.uniform(0.1, 0.5))

    def _detect_captcha(self):
        driver = self.driver
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and ("recaptcha" in src or "hcaptcha" in src):
                return True
        return False

    def _wait_for_captcha(self, max_wait=40):
        # Placeholder for real CAPTCHA solving: here we just wait & alert
        logging.info("CAPTCHA detected! Waiting for manual completion or solver API (not integrated).")
        waited = 0
        while self._detect_captcha() and waited < max_wait:
            time.sleep(3)
            waited += 3

    def perform(self):
        try:
            self._init_driver()
            self.driver.get(self.url)
            time.sleep(random.uniform(2, 4))
            # Check for CAPTCHA
            if self._detect_captcha():
                self._wait_for_captcha()
            # Simulate human action
            self._simulate_human_behavior()
            # Random wait after actions
            time.sleep(random.uniform(1.5, 3.5))
            return True, "Impression completed"
        except Exception as e:
            logging.error(f"Browser automation failed: {e}")
            return False, str(e)
        finally:
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass

# ====================== TASK QUEUE AND WORKER ====================
class Task:
    def __init__(self, url, user_id, chat_id):
        self.url = url
        self.user_id = user_id
        self.chat_id = chat_id
        self.timestamp = datetime.datetime.utcnow()

class BotTaskQueue:
    def __init__(self):
        self.queue = Queue()
        self.active = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while self.active:
            task = self.queue.get()
            if task is None:
                break
            logging.info(f"Processing task: {task.url} for user {task.user_id}")
            proxy = proxy_manager.get_random_proxy()
            browser = HumanLikeBrowser(task.url, proxy=proxy, headless=True)
            success, msg = browser.perform()
            asyncio.run(send_task_result(task, success, msg))
            self.queue.task_done()

    def add_task(self, task):
        self.queue.put(task)

    def stop(self):
        self.active = False
        self.queue.put(None)

task_queue = BotTaskQueue()

# ====================== TELEGRAM BOT CORE ========================
app = Client("beast_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def send_task_result(task, success, msg):
    try:
        if success:
            await app.send_message(task.chat_id,
                f"✅ [Impression Complete] Link visited successfully at {datetime.datetime.now().strftime('%H:%M:%S')}!\n\n📈 {msg}"
            )
        else:
            await app.send_message(task.chat_id,
                f"❌ [Failed] Link impression failed: {msg}"
            )
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

# =============== BOT COMMANDS ===============

@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply(
        "👋 Welcome to *BEAST LINK BOT v4.0* (Ultra Stealth).\n\n"
        "🚀 This bot automates Linkvertise impressions using rotating proxies, advanced browser fingerprinting, and deep human simulation.\n"
        "🛡️ Cross-platform, optimized for Termux.\n\n"
        "📖 Use /help for commands.\n"
        "🤖 Use /link <url> to start an impression."
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await message.reply(
        "**🛠 Beast Bot Commands:**\n"
        "`/link <linkvertise_url>` – Start a new impression\n"
        "`/status` – System health and proxy count\n"
        "`/reloadproxies` – Reload proxies from file\n"
        "`/start` – Start message\n"
        "`/help` – This help panel"
    )

@app.on_message(filters.command("status"))
async def status_cmd(client, message: Message):
    count = proxy_manager.get_count()
    await message.reply(
        f"🔌 Total proxies loaded: {count}\n"
        f"🧠 System healthy. Ready for impression automation."
    )

@app.on_message(filters.command("reloadproxies"))
async def reloadproxies_cmd(client, message: Message):
    proxy_manager.reload()
    count = proxy_manager.get_count()
    await message.reply(f"♻️ Proxies reloaded. Now loaded: {count}")

@app.on_message(filters.command("link"))
async def link_cmd(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Usage: `/link <linkvertise_url>`")
        return
    url = args[1]
    # Validate Linkvertise domain
    if not ("linkvertise.com" in url or "link-to.net" in url):
        await message.reply("❌ Only Linkvertise URLs are supported.")
        return
    now = datetime.datetime.now().strftime("%H:%M:%S")
    await message.reply(f"🧠 [{now}] Task queued for: `{url}`\n\n🌐 Rotating proxies, human browser, and smart fingerprinting...")
    # Queue the task for background processing
    task = Task(url, message.from_user.id, message.chat.id)
    task_queue.add_task(task)

# ====================== BOT RUNNER =============================
if __name__ == "__main__":
    print("🚀 BEAST LINK BOT v4.0 (Ultra Stealth) Running on Termux...")
    app.run()

    # Graceful shutdown
    task_queue.stop()