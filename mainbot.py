import random
import time
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from selenium_stealth import stealth

# =============== TELEGRAM BOT CONFIG ===============
API_ID = "24235215" # ⚠️ Replace with your own
API_HASH = "f344f64fc2e54099684b09273a4d445b"
BOT_TOKEN = "your_bot_token"

app = Client("beast_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# =============== GET RANDOM PROXY ===============
def get_random_proxy():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            return None
        return random.choice(proxies)
    except Exception as e:
        print(f"[❌] Proxy error: {str(e)}")
        return None

# =============== FAKE HUMAN INTERACTION ===============
def simulate_human_behavior(driver):
    try:
        actions = ActionChains(driver)
        # Move mouse in random pattern
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(50, 250)
            y_offset = random.randint(20, 200)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.8, 1.8))
        # Randomly click on page elements
        elements = driver.find_elements(By.XPATH, "//*")
        random.shuffle(elements)
        for el in elements[:random.randint(1, 5)]:
            try:
                actions.move_to_element(el).click().perform()
                time.sleep(random.uniform(0.3, 1.2))
            except Exception:
                continue
        # Scroll page in distinct steps
        scroll_heights = [0.15, 0.3, 0.5, 0.7, 1.0]
        for level in scroll_heights:
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {level});")
            time.sleep(random.uniform(1.3, 2.8))
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(0.8, 1.5))
    except Exception as e:
        print(f"[⚠️] Human simulation error: {str(e)}")

# =============== ANTI-DETECTION PATCH ===============
def apply_stealth_settings(driver, ua):
    try:
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=False
        )
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": ua})
        width = random.randint(1000, 1600)
        height = random.randint(700, 1200)
        driver.set_window_size(width, height)
    except Exception as e:
        print(f"[⚠️] Stealth error: {str(e)}")

# =============== CAPTCHA BYPASS (DEMO PLACEHOLDER) ===============
def try_solve_captcha(driver):
    # Placeholder: Integrate with a captcha solving service like 2captcha, anti-captcha, etc.
    # For now, just detect if there's a known captcha and pause
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        src = iframe.get_attribute("src")
        if src and ("recaptcha" in src or "hcaptcha" in src):
            print("[⚠️] CAPTCHA detected! Manual solve required or integrate captcha solver.")
            time.sleep(random.uniform(10, 20))  # Simulate waiting for manual or API solve

# =============== LINK VISIT CORE ===============
def visit_link(url):
    proxy = get_random_proxy()
    if not proxy:
        print("[❌] No proxy found.")
        return False

    ua = UserAgent().random
    options = uc.ChromeOptions()
    options.add_argument(f"--proxy-server=http://{proxy}")
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(random.uniform(1, 2.5))

        apply_stealth_settings(driver, ua)
        time.sleep(random.uniform(2, 4))

        try_solve_captcha(driver)
        simulate_human_behavior(driver)
        time.sleep(random.uniform(2.5, 5.5))

        driver.quit()
        return True
    except Exception as e:
        print(f"[ERROR] Visit failed: {str(e)}")
        try:
            if driver: driver.quit()
        except: pass
        return False

# =============== COMMAND: /start ===============
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "👋 Welcome to the *BEAST LINK BOT v3.0* (Advanced Stealth).\n\n"
        "🚀 This bot auto-clicks Linkvertise links with rotating proxies, true humanization, and stealth bypass.\n"
        "🔒 Undetectable: patched browser fingerprint, random mouse/clicks, rotating UA & proxy, and CAPTCHA ready!\n\n"
        "🧪 Use /link <url> to start.\n"
        "ℹ️ Use /help for more commands."
    )

# =============== COMMAND: /help ===============
@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply(
        "**🛠 Beast Bot Commands:**\n"
        "`/link <linkvertise_url>` – Start automated visit\n"
        "`/status` – Show total proxies available\n"
        "`/start` – Welcome message\n"
        "`/help` – This help panel"
    )

# =============== COMMAND: /status ===============
@app.on_message(filters.command("status"))
async def status(client, message: Message):
    try:
        with open("proxies.txt", "r") as f:
            count = len([line for line in f if line.strip()])
        await message.reply(f"🔌 Total proxies loaded: {count}\n🧠 System healthy. Ready to boost impressions.")
    except Exception as e:
        await message.reply("⚠️ Error loading proxies.txt. Make sure the file exists.")

# =============== COMMAND: /link ===============
@app.on_message(filters.command("link"))
async def handle_link(client, message: Message):
    try:
        parts = message.text.strip().split(" ")
        if len(parts) < 2:
            await message.reply("❌ Please send a link like:\n`/link https://linkvertise.com/...`")
            return
        url = parts[1]
        now = datetime.datetime.now().strftime("%H:%M:%S")
        await message.reply(f"🧠 [{now}] Beast is executing...\n\n🌐 Visiting: `{url}`\n⏳ Using rotating proxies, user-agent, and human actions...")

        result = visit_link(url)
        if result:
            await message.reply("✅ Link visited successfully!\n📈 Impressions added.\n🤖 Fully undetected & humanized!")
        else:
            await message.reply("❌ Link visit failed.\nCheck proxy/link or try again later.")

    except Exception as e:
        await message.reply(f"⚠️ Unexpected error: {str(e)}")

# =============== RUN THE BOT ===============
if __name__ == "__main__":
    print("🚀 BEAST BOT v3.0 Advanced Stealth Running...")
    app.run()
