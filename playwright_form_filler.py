import asyncio
import random
import time
import os
import re
import sys
import json
import argparse
from datetime import datetime
from faker import Faker
from playwright.async_api import async_playwright

# Parse argumen command line
parser = argparse.ArgumentParser(description='Pengisi otomatis Google Form Universal')
parser.add_argument('--url', type=str, help='URL Google Form')
parser.add_argument('--responses', type=int, help='Jumlah total respons yang diinginkan')
parser.add_argument('--per-session', type=int, help='Jumlah respons per sesi')
parser.add_argument('--headless', action='store_true', help='Jalankan browser dalam mode headless (tanpa UI)')
parser.add_argument('--proxy-file', type=str, help='File dengan daftar proxy (format: protokol://username:password@host:port per baris)')
parser.add_argument('--language', type=str, default='id_ID', help='Kode bahasa untuk generasi data (default: id_ID)')
args = parser.parse_args()

# Inisialisasi Faker untuk data lokalisasi
fake = Faker(args.language if args.language else 'id_ID')

# URL dan jumlah respons
FORM_URL = args.url if args.url else input("Masukkan URL Google Form: ") if len(sys.argv) < 2 else sys.argv[1]
TOTAL_RESPONSES = args.responses if args.responses else int(input("Jumlah total respons yang diinginkan: ") if len(sys.argv) < 3 else sys.argv[2])
MAX_PER_SESSION = args.per_session if args.per_session else int(input("Jumlah respons per sesi (disarankan 20): ") if len(sys.argv) < 4 else sys.argv[3] or "20")
HEADLESS_MODE = args.headless

# Konfigurasi proxy
PROXIES = []
if args.proxy_file and os.path.exists(args.proxy_file):
    with open(args.proxy_file, 'r') as f:
        PROXIES = [line.strip() for line in f.readlines() if line.strip()]
    print(f"Loaded {len(PROXIES)} proxies from {args.proxy_file}")

# Konfigurasi anti-deteksi
MIN_TYPING_DELAY = 30  # ms
MAX_TYPING_DELAY = 150  # ms
MIN_WAIT_SHORT = 400  # ms
MAX_WAIT_SHORT = 1500  # ms
MIN_WAIT_MEDIUM = 800  # ms
MAX_WAIT_MEDIUM = 3000  # ms
MIN_WAIT_LONG = 2000  # ms
MAX_WAIT_LONG = 5000  # ms
MIN_SESSION_PAUSE = 600  # detik (10 menit)
MAX_SESSION_PAUSE = 1800  # detik (30 menit)

# User-Agent yang realistis
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
]

MALE_FIRST_NAMES = [
    "Aaron", "Adrian", "Ahmad", "Aidan", "Aksel", "Albert", "Alex", "Alif", "Andi", "Andrew",
    "Anthony", "Arif", "Arthur", "Bagus", "Bayu", "Benjamin", "Brian", "Caleb", "Carlos", "Daniel",
    "David", "Deni", "Dimas", "Dylan", "Edward", "Eko", "Ethan", "Fajar", "Felix", "Gabriel",
    "George", "Gunawan", "Hadi", "Henry", "Ilham", "Irfan", "Isaac", "Jack", "James", "Jason",
    "Jonathan", "Joseph", "Joshua", "Julian", "Kevin", "Leo", "Liam", "Logan", "Lucas", "Luke",
    "Matthew", "Michael", "Muhammad", "Nathan", "Nicholas", "Noah", "Oliver", "Owen", "Rafael", "Rafi",
    "Rayhan", "Ryan", "Samuel", "Theo", "Thomas", "Tomi", "William", "Yusuf", "Zayn", "Zidan",
]

FEMALE_FIRST_NAMES = [
    "Aaliyah", "Abigail", "Adeline", "Aisyah", "Alexa", "Alice", "Alya", "Amanda", "Amelia", "Anisa",
    "Anna", "Ariana", "Ashley", "Aubrey", "Aulia", "Aurora", "Ava", "Avery", "Ayu", "Bella",
    "Camila", "Charlotte", "Chloe", "Clara", "Citra", "Dewi", "Dinda", "Diora", "Ella", "Emily",
    "Emma", "Evelyn", "Fatima", "Fitri", "Gabriella", "Grace", "Hana", "Hannah", "Indah", "Isabella",
    "Jasmine", "Julia", "Kayla", "Kartika", "Layla", "Leah", "Lestari", "Lily", "Luna", "Maya",
    "Mia", "Nabila", "Nadia", "Naomi", "Natalie", "Nurul", "Olivia", "Putri", "Rania", "Rina",
    "Sabrina", "Safira", "Sari", "Sophia", "Tiara", "Violet", "Wulan", "Yuni", "Zahra", "Zoe",
]

MALE_LAST_NAMES = [
    "Adams", "Anderson", "Brown", "Campbell", "Carter", "Clark", "Collins", "Cruz", "Davis", "Diaz",
    "Evans", "Foster", "Garcia", "Gonzalez", "Gray", "Green", "Hall", "Harris", "Hernandez", "Hill",
    "Howard", "Hughes", "Jackson", "James", "Johnson", "Jones", "King", "Lee", "Lewis", "Martin",
    "Martinez", "Miller", "Mitchell", "Moore", "Morgan", "Morris", "Murphy", "Nelson", "Nguyen", "Parker",
    "Patel", "Perez", "Peterson", "Phillips", "Pratama", "Rahman", "Ramirez", "Reed", "Richardson", "Rivera",
    "Roberts", "Robinson", "Rodriguez", "Sanchez", "Scott", "Setiawan", "Sharma", "Singh", "Smith", "Stewart",
    "Sullivan", "Taylor", "Thomas", "Thompson", "Turner", "Walker", "Ward", "Watson", "White", "Wijaya",
    "Williams", "Wilson", "Wright", "Young", "Yunus", "Nugroho", "Hidayat", "Kusuma", "Firmansyah", "Maulana",
    "Fauzi", "Saputra", "Putra", "Gunawan", "Prakoso", "Wibowo", "Permana", "Ramadhan", "Siregar", "Herlambang",
]

FEMALE_LAST_NAMES = [
    "Azzahra", "Cahyani", "Clarke", "Collins", "Dewanti", "Fitriani", "Garcia", "Grace", "Handayani", "Hasanah",
    "Hernandez", "Hill", "Hutami", "Indriani", "Iskandar", "Julianti", "Kirana", "Kusumawati", "Lestari", "Maharani",
    "Maulida", "Monroe", "Nainggolan", "Naomi", "Novianti", "Nugraheni", "Oktaviani", "Permatasari", "Prameswari", "Putri",
    "Rahma", "Rahmawati", "Ramadhani", "Rizqiani", "Roberts", "Rodriguez", "Rosalina", "Salsabila", "Sanchez", "Saputri",
    "Sari", "Setyaningsih", "Shafira", "Sophia", "Sukmawati", "Sullivan", "Susanti", "Taylor", "Utami", "Valentina",
    "Wardhani", "Wati", "Wijayanti", "Wulandari", "Yolanda", "Yuliana", "Yusnita", "Zahara", "Amalia", "Puspitasari",
    "Anggraini", "Febriani", "Aulia", "Nuraini", "Kartikasari", "Widyaningsih", "Melawati", "Paramitha", "Ratnasari", "Safitri",
]

MALE_PREFIX_TITLES = ["Mr.", "H.", "Dr.", "Ir."]
FEMALE_PREFIX_TITLES = ["Ms.", "Mrs.", "Dr.", "Dra."]
NEUTRAL_SUFFIX_TITLES = [
    "S.H.", "S.Kom.", "S.E.", "S.Sos.", "S.Pd.", "S.T.", "S.Farm.", "M.Kom.", "M.M.", "M.Si.",
    "M.Pd.", "M.H.", "M.Farm", "M.Farm.", "A.Md.", "A.Md.Kom.", "S.Ked.", "drg.", "apt.",
]

# Konfigurasi logging
import logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
log_filename = os.path.join(LOG_DIR, f"formfiller_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FormFiller")

# Fungsi untuk simulasi perilaku manusia
async def human_delay_short():
    """Jeda pendek yang manusiawi"""
    await asyncio.sleep(random.randint(MIN_WAIT_SHORT, MAX_WAIT_SHORT) / 1000)

async def human_delay_medium():
    """Jeda medium yang manusiawi"""
    await asyncio.sleep(random.randint(MIN_WAIT_MEDIUM, MAX_WAIT_MEDIUM) / 1000)

async def human_delay_long():
    """Jeda lama yang manusiawi"""
    await asyncio.sleep(random.randint(MIN_WAIT_LONG, MAX_WAIT_LONG) / 1000)

async def natural_scroll(page, distance):
    """Scroll dengan perilaku alami"""
    steps = random.randint(5, 15)
    for i in range(steps):
        step = distance / steps
        await page.evaluate(f"window.scrollBy(0, {step})")
        await asyncio.sleep(random.randint(30, 100) / 1000)

async def human_type(page, selector, text):
    """Ketik teks dengan pola manusia"""
    await page.focus(selector)
    await human_delay_short()  # Sedikit jeda sebelum mulai mengetik
    
    for char in text:
        await page.keyboard.type(char, delay=random.randint(MIN_TYPING_DELAY, MAX_TYPING_DELAY))
        
        # Kadang-kadang tambahkan jeda yang lebih lama (seperti berpikir)
        if random.random() < 0.1:  # 10% kemungkinan
            await asyncio.sleep(random.randint(200, 500) / 1000)

async def human_click(page, selector):
    """Klik elemen dengan pola manusia"""
    # Temukan elemen
    element = await page.query_selector(selector)
    if not element:
        raise Exception(f"Elemen tidak ditemukan: {selector}")
    
    # Dapatkan bounding box
    box = await element.bounding_box()
    if not box:
        raise Exception(f"Tidak bisa mendapatkan posisi elemen: {selector}")
    
    # Gerakkan mouse ke posisi acak dalam elemen
    x = box['x'] + box['width'] * random.uniform(0.1, 0.9)
    y = box['y'] + box['height'] * random.uniform(0.1, 0.9)
    
    # Gerakkan mouse dengan langkah manusiawi
    await page.mouse.move(x, y, steps=random.randint(5, 15))
    
    # Jeda sebentar seperti sedang berpikir
    await human_delay_short()
    
    # Klik
    await page.mouse.click(x, y)

async def human_select_option(page, choice_text):
    """Pilih opsi dari daftar dengan perilaku manusia"""
    try:
        # Tunggu sampai halaman stabil
        await page.wait_for_load_state("networkidle")
        
        # Coba metode yang berbeda untuk menemukan dan mengklik elemen
        found = False
        
        # Metode 1: Cari berdasarkan teks yang tepat (dengan JavaScript)
        js_script = f"""
        () => {{
            const walkDOM = (node, target) => {{
                if (node.nodeType === Node.TEXT_NODE) {{
                    if (node.textContent.trim() === "{choice_text}") {{
                        // Temukan elemen yang dapat diklik (parent atau sibling)
                        let clickable = node.parentNode;
                        while (clickable && !clickable.click) {{
                            clickable = clickable.parentNode;
                        }}
                        if (clickable && clickable.click) {{
                            clickable.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                            setTimeout(() => clickable.click(), 100);
                            return true;
                        }}
                    }}
                }} else {{
                    for (const child of node.childNodes) {{
                        if (walkDOM(child, target)) return true;
                    }}
                }}
                return false;
            }};
            
            return walkDOM(document.body, "{choice_text}");
        }}
        """
        
        # Coba klik dengan JavaScript
        found = await page.evaluate(js_script)
        if found:
            await human_delay_medium()
            return True
            
        # Metode 2: Cari dengan substring
        if not found:
            short_choice = choice_text.split(" ")[0:3]  # Ambil 3 kata pertama
            short_text = " ".join(short_choice)
            
            # Cari semua elemen yang terlihat dan berisi teks tersebut
            elements = await page.query_selector_all('div[role="radio"], div[role="checkbox"]')
            
            for element in elements:
                text = await element.text_content()
                if short_text in text:
                    # Scroll ke elemen
                    await element.scroll_into_view_if_needed()
                    await human_delay_short()
                    
                    # Klik dengan gerakan mouse yang alami
                    box = await element.bounding_box()
                    if box:
                        x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
                        y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
                        await page.mouse.move(x, y, steps=random.randint(3, 8))
                        await human_delay_short()
                        await page.mouse.click(x, y)
                        await human_delay_medium()
                        return True
        
        # Metode 3: Coba cari dengan xpath
        if not found:
            # Cari elemen yang mengandung teks yang mirip
            xpath = f"//div[contains(text(), '{choice_text.split(' ')[0]}')]"
            element = await page.query_selector(xpath)
            if element:
                await element.scroll_into_view_if_needed()
                await human_delay_short()
                await element.click()
                await human_delay_medium()
                return True
        
        print(f"Tidak bisa menemukan pilihan: {choice_text}")
        return False
    
    except Exception as e:
        print(f"Error saat memilih opsi '{choice_text}': {str(e)}")
        return False

async def submit_form(page):
    """Identifikasi aksi akhir form dengan aman."""
    try:
        button_info = await inspect_action_buttons(page)
        labels = [item["label"] for item in button_info]
        logger.info(f"Tombol aksi terdeteksi: {labels}")

        for item in button_info:
            label = item["label"].lower()
            if "kosongkan formulir" in label or "clear form" in label:
                logger.warning("Tombol 'Kosongkan formulir' terdeteksi. Tidak akan diklik.")

        submit_labels = {"kirim", "submit", "send"}
        next_labels = {"berikutnya", "next"}

        submit_candidates = [item for item in button_info if item["label"].lower() in submit_labels]
        next_candidates = [item for item in button_info if item["label"].lower() in next_labels]

        if next_candidates and not submit_candidates:
            logger.warning("Form tampak multi-halaman karena tombol 'Berikutnya' terdeteksi. Alur ini tidak dilanjutkan.")
            return False

        if not submit_candidates:
            logger.warning("Tombol submit eksplisit tidak ditemukan. Membatalkan agar tidak salah klik.")
            return False

        submit_button = submit_candidates[0]["element"]
        await submit_button.scroll_into_view_if_needed()
        await human_delay_medium()

        box = await submit_button.bounding_box()
        if not box:
            logger.warning("Posisi tombol submit tidak bisa dibaca.")
            return False

        x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
        y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
        await page.mouse.move(x, y, steps=random.randint(5, 10))
        await human_delay_medium()
        await page.mouse.click(x, y)
        return True
    except Exception as e:
        print(f"Error saat submit form: {str(e)}")
        return False

def normalize_action_label(label):
    """Normalisasi label tombol agar cocok meski ada ikon/whitespace tambahan."""
    return " ".join(re.sub(r"[^\w\s-]", " ", (label or "").lower()).split())

async def safe_get_page_content(page, retries=5, delay=0.5):
    """Ambil HTML halaman dengan retry saat page masih bernavigasi."""
    last_error = None
    for _ in range(retries):
        try:
            return await page.content()
        except Exception as e:
            last_error = e
            await asyncio.sleep(delay)
    raise last_error

async def wait_for_form_ready(page):
    """Tunggu sampai halaman form stabil setelah navigasi antar page."""
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=10000)
    except Exception:
        pass

    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    for _ in range(10):
        try:
            await page.wait_for_selector('form, div[role="radiogroup"], input[type="text"], textarea', timeout=1500)
            return True
        except Exception:
            await asyncio.sleep(0.4)
    return False

async def get_page_signature(page):
    """Ambil fingerprint ringan halaman aktif untuk mendeteksi progres navigasi."""
    try:
        return await page.evaluate("""
            () => {
                const title = document.title || "";
                const bodyText = (document.body?.innerText || "").replace(/\\s+/g, " ").trim().slice(0, 1200);
                const nextButton = Array.from(document.querySelectorAll('div[role="button"], span[role="button"]'))
                    .map((el) => (el.innerText || el.textContent || "").trim())
                    .filter(Boolean)
                    .join(" | ");
                return `${location.href}||${title}||${bodyText}||${nextButton}`;
            }
        """)
    except Exception:
        try:
            return f"{page.url}||fallback"
        except Exception:
            return "unknown-page"

async def wait_for_page_signature_change(page, previous_signature, timeout_ms=6000):
    """Tunggu sampai fingerprint halaman berubah."""
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        current_signature = await get_page_signature(page)
        if current_signature != previous_signature:
            return True
        await asyncio.sleep(0.25)
    return False

async def click_action_button_with_retry(page, button_item, action_name):
    """Klik tombol aksi dengan beberapa strategi dan verifikasi perubahan halaman."""
    previous_signature = await get_page_signature(page)
    attempts = [
        "human_click",
        "element_click",
        "dom_click",
    ]

    for attempt in attempts:
        try:
            await button_item["element"].scroll_into_view_if_needed()
        except Exception:
            pass

        try:
            await natural_scroll_improved(page, 180)
        except Exception:
            pass

        await human_delay_short()

        try:
            if attempt == "human_click":
                await human_click_improved(page, button_item["element"])
            elif attempt == "element_click":
                await button_item["element"].click(force=True)
            else:
                await button_item["element"].evaluate("(el) => el.click()")
        except Exception as e:
            logger.warning(f"Gagal klik {action_name} dengan metode {attempt}: {str(e)}")
            continue

        await wait_for_form_ready(page)
        changed = await wait_for_page_signature_change(page, previous_signature, timeout_ms=5000)
        if changed:
            return True

        logger.warning(f"Klik {action_name} dengan metode {attempt} tidak mengubah halaman.")

    return False

async def handle_next_or_submit(page):
    """Klik tombol Next/Submit yang terlihat dengan prioritas Next lebih dulu."""
    try:
        buttons = await inspect_action_buttons(page)
        labels = [item["label"] for item in buttons]
        logger.info(f"Tombol aksi terdeteksi: {labels}")

        submit_labels = {"kirim", "submit", "send"}
        next_labels = {"berikutnya", "next"}

        submit_btn = None
        next_btn = None

        for item in buttons:
            normalized_label = normalize_action_label(item["label"])

            if normalized_label in submit_labels:
                submit_btn = item
            elif normalized_label in next_labels:
                next_btn = item

        if next_btn:
            logger.info("➡️ Next page detected")
            moved = await click_action_button_with_retry(page, next_btn, "Next")
            if moved:
                await asyncio.sleep(0.8)
                return "next"
            logger.warning("Tombol Next terdeteksi tetapi halaman tidak berubah.")
            return "none"

        if submit_btn:
            logger.info("✅ Submit detected")
            moved = await click_action_button_with_retry(page, submit_btn, "Submit")
            if moved:
                return "submit"
            logger.warning("Tombol Submit terdeteksi tetapi halaman tidak berubah.")
            return "none"

        logger.warning("⚠️ No action button found")
        return "none"

    except Exception as e:
        logger.error(f"Error handle_next_or_submit: {e}")
        return "none"

async def inspect_action_buttons(page):
    """Ambil tombol aksi yang terlihat di halaman untuk diagnosis."""
    buttons = []
    elements = await page.query_selector_all('div[role="button"], span[role="button"]')
    for element in elements:
        try:
            text = (await element.inner_text() or "").strip()
            if not text:
                continue
            box = await element.bounding_box()
            if not box:
                continue
            buttons.append({
                "label": " ".join(text.split()),
                "element": element,
                "y": box["y"],
            })
        except Exception:
            continue
    return sorted(buttons, key=lambda item: item["y"])

async def detect_page_action_state(page):
    """Ringkas aksi utama yang tersedia pada halaman aktif."""
    buttons = await inspect_action_buttons(page)
    labels = [normalize_action_label(item["label"]) for item in buttons]
    submit_labels = {"kirim", "submit", "send"}
    next_labels = {"berikutnya", "next"}

    return {
        "buttons": buttons,
        "labels": labels,
        "has_next": any(label in next_labels for label in labels),
        "has_submit": any(label in submit_labels for label in labels),
    }

async def is_element_visible(element):
    """Cek apakah elemen benar-benar terlihat di halaman aktif."""
    try:
        box = await element.bounding_box()
        if not box:
            return False
        if box["width"] <= 0 or box["height"] <= 0:
            return False
        return await element.evaluate("""
            (el) => {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return (
                    style &&
                    style.visibility !== "hidden" &&
                    style.display !== "none" &&
                    rect.width > 0 &&
                    rect.height > 0
                );
            }
        """)
    except Exception:
        return False

async def extract_question_title(element):
    """Ambil judul pertanyaan dari container terdekat."""
    try:
        title = await element.evaluate("""
            (el) => {
                const selectors = [
                    'div[class*="freebirdFormviewerComponentsQuestionBaseTitle"]',
                    '[role="heading"]'
                ];

                let node = el;
                for (let depth = 0; node && depth < 8; depth += 1, node = node.parentElement) {
                    for (const selector of selectors) {
                        const candidate = node.querySelector(selector);
                        if (candidate) {
                            const text = (candidate.innerText || candidate.textContent || "").trim();
                            if (text) {
                                return text;
                            }
                        }
                    }
                }
                return "";
            }
        """)
        cleaned_title = (title or "").strip()
        cleaned_title = re.sub(r'\n\s*\*+\s*$', '', cleaned_title)
        cleaned_title = re.sub(r'\s*\*+\s*$', '', cleaned_title)
        cleaned_title = " ".join(cleaned_title.split())
        return cleaned_title
    except Exception:
        return ""

async def extract_option_label(option_element):
    """Ambil label opsi radio/checkbox dengan prioritas ke label lokal, bukan seluruh grup."""
    try:
        label = await option_element.evaluate("""
            (el) => {
                const candidates = [
                    el.getAttribute("data-value"),
                    el.getAttribute("aria-label"),
                    el.innerText,
                    el.textContent,
                ];

                const localSelectors = [
                    '[dir="auto"]',
                    'span',
                    'div'
                ];

                for (const selector of localSelectors) {
                    const nodes = el.querySelectorAll(selector);
                    for (const node of nodes) {
                        const text = (node.innerText || node.textContent || "").trim();
                        if (text && text.length < 120) {
                            candidates.push(text);
                        }
                    }
                }

                for (const raw of candidates) {
                    const cleaned = (raw || "").trim();
                    if (cleaned) {
                        return cleaned;
                    }
                }
                return "";
            }
        """)
        return " ".join((label or "").split())
    except Exception:
        return ""

class FormAnalyzer:
    def __init__(self):
        self.questions = []
        self.sections = []
        self.text_inputs = []
        self.radio_groups = []
        self.checkbox_groups = []
        self.dropdown_groups = []
        self.language = 'unknown'
        self.debug_mode = False

    def _question_mentions_gender(self, question_text):
        normalized_text = normalize_action_label(question_text)
        gender_keywords = [
            "jenis kelamin",
            "gender",
            "sex",
            "jenis gender",
        ]
        return any(keyword in normalized_text for keyword in gender_keywords)

    def _classify_gender_option(self, option_text):
        normalized_option = normalize_action_label(option_text)
        male_markers = [
            "laki laki",
            "laki-laki",
            "pria",
            "male",
            "man",
            "boy",
        ]
        female_markers = [
            "perempuan",
            "wanita",
            "female",
            "woman",
            "girl",
        ]

        if any(marker in normalized_option for marker in male_markers):
            return "male"
        if any(marker in normalized_option for marker in female_markers):
            return "female"
        return None

    def _choose_gender_option(self, options):
        classified_options = []
        for option in options:
            gender_label = self._classify_gender_option(option)
            if gender_label:
                classified_options.append((option, gender_label))

        if not classified_options:
            return None

        return random.choice(classified_options)

    def _generate_gendered_name(self, selected_gender):
        if selected_gender == "male":
            first_name_pool = MALE_FIRST_NAMES
            last_name_pool = MALE_LAST_NAMES
            prefix_pool = MALE_PREFIX_TITLES
        elif selected_gender == "female":
            first_name_pool = FEMALE_FIRST_NAMES
            last_name_pool = FEMALE_LAST_NAMES
            prefix_pool = FEMALE_PREFIX_TITLES
        else:
            first_name_pool = MALE_FIRST_NAMES + FEMALE_FIRST_NAMES
            last_name_pool = MALE_LAST_NAMES + FEMALE_LAST_NAMES
            prefix_pool = MALE_PREFIX_TITLES + FEMALE_PREFIX_TITLES

        first_name = random.choice(first_name_pool)
        name_parts = [first_name]

        if random.random() < 0.35:
            middle_candidates = [name for name in first_name_pool if name != first_name]
            if middle_candidates:
                name_parts.append(random.choice(middle_candidates))

        last_name_count = 1 if random.random() < 0.8 else 2
        name_parts.extend(random.sample(last_name_pool, k=last_name_count))

        full_name = " ".join(name_parts)

        if random.random() < 0.18:
            full_name = f"{random.choice(prefix_pool)} {full_name}"

        if random.random() < 0.22:
            suffix_count = 1 if random.random() < 0.85 else 2
            suffixes = random.sample(NEUTRAL_SUFFIX_TITLES, k=suffix_count)
            full_name = f"{full_name}, {' '.join(suffixes)}"

        return full_name

    def prepare_response_context(self, questions, response_context=None):
        """Siapkan konteks respons agar jawaban lintas-pertanyaan tetap konsisten."""
        if response_context is None:
            response_context = {}

        if response_context.get("selected_gender"):
            return response_context

        for question in questions:
            if question.get('type') not in ['radio', 'dropdown']:
                continue
            if not self._question_mentions_gender(question.get('question', '')):
                continue

            selected = self._choose_gender_option(question.get('options', []))
            if not selected:
                continue

            selected_option, selected_gender = selected
            response_context["gender_answer"] = selected_option
            response_context["selected_gender"] = selected_gender
            break

        return response_context
        
    async def detect_language(self, page):
        """Mendeteksi bahasa formulir"""
        page_content = await safe_get_page_content(page)
        
        # Cek bahasa berdasarkan kata-kata umum
        language_markers = {
            'id': ['Nama', 'Terima kasih', 'Kirim', 'Lanjutkan', 'Wajib'],
            'en': ['Name', 'Thank you', 'Submit', 'Continue', 'Required'],
            'es': ['Nombre', 'Gracias', 'Enviar', 'Continuar', 'Obligatorio'],
            'fr': ['Nom', 'Merci', 'Envoyer', 'Continuer', 'Obligatoire'],
            'de': ['Name', 'Vielen Dank', 'Senden', 'Weiter', 'Erforderlich']
        }
        
        lang_scores = {lang: 0 for lang in language_markers}
        
        for lang, markers in language_markers.items():
            for marker in markers:
                if marker in page_content:
                    lang_scores[lang] += 1
        
        # Tentukan bahasa dengan skor tertinggi
        if max(lang_scores.values()) > 0:
            self.language = max(lang_scores.items(), key=lambda x: x[1])[0]
            logger.info(f"Bahasa formulir terdeteksi: {self.language}")
        else:
            self.language = 'en'  # Default ke bahasa Inggris
            logger.info(f"Bahasa tidak terdeteksi, menggunakan default: {self.language}")
        
        return self.language
        
    async def analyze_form(self, page, debug_mode=False):
        """Analisis struktur formulir Google dengan dukungan lebih banyak jenis pertanyaan"""
        self.debug_mode = debug_mode
        logger.info("Menganalisis struktur formulir...")
        await wait_for_form_ready(page)
        self.questions = []
        self.sections = []
        self.text_inputs = []
        self.radio_groups = []
        self.checkbox_groups = []
        self.dropdown_groups = []
        
        # Deteksi bahasa formulir
        await self.detect_language(page)
        
        # Deteksi input teks
        raw_text_inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"], input[type="number"], textarea')
        self.text_inputs = [element for element in raw_text_inputs if await is_element_visible(element)]
        logger.info(f"Terdeteksi {len(self.text_inputs)} input teks/email/nomor/area teks")
        
        # Deteksi pertanyaan dengan opsi radio
        raw_radio_groups = await page.query_selector_all('div[role="radiogroup"]')
        radio_groups = [element for element in raw_radio_groups if await is_element_visible(element)]
        logger.info(f"Terdeteksi {len(radio_groups)} grup radio (pilihan tunggal)")
        
        # Ambil teks pertanyaan dan opsi untuk setiap grup radio
        for i, group in enumerate(radio_groups):
            try:
                question_text = await extract_question_title(group)
                if not question_text:
                    continue

                options_elems = await group.query_selector_all('div[role="radio"]')
                options = []
                for option in options_elems:
                    if not await is_element_visible(option):
                        continue
                    option_text = await extract_option_label(option)
                    if option_text:
                        options.append(option_text)

                if debug_mode:
                    logger.debug(f"Radio group: {question_text.strip()} - Options: {options}")

                self.radio_groups.append({
                    'question': question_text.strip(),
                    'options': options,
                    'element': group
                })
            except Exception as e:
                logger.error(f"Error saat menganalisis grup radio {i}: {str(e)}")
        
        # Deteksi pertanyaan checkbox
        raw_checkbox_groups = await page.query_selector_all('div[role="list"][jsname="L8DVEb"]')
        checkbox_groups = [element for element in raw_checkbox_groups if await is_element_visible(element)]
        logger.info(f"Terdeteksi {len(checkbox_groups)} grup checkbox (pilihan ganda)")
        
        # Ambil teks pertanyaan dan opsi untuk setiap grup checkbox
        for i, group in enumerate(checkbox_groups):
            try:
                question_text = await extract_question_title(group)
                if not question_text:
                    continue

                options_elems = await group.query_selector_all('div[role="checkbox"]')
                options = []
                for option in options_elems:
                    if not await is_element_visible(option):
                        continue
                    option_text = await extract_option_label(option)
                    if option_text:
                        options.append(option_text)

                if debug_mode:
                    logger.debug(f"Checkbox group: {question_text.strip()} - Options: {options}")

                self.checkbox_groups.append({
                    'question': question_text.strip(),
                    'options': options,
                    'element': group
                })
            except Exception as e:
                logger.error(f"Error saat menganalisis grup checkbox {i}: {str(e)}")
        
        # Deteksi dropdown
        raw_dropdown_groups = await page.query_selector_all('div[role="listbox"]')
        dropdown_groups = [element for element in raw_dropdown_groups if await is_element_visible(element)]
        logger.info(f"Terdeteksi {len(dropdown_groups)} dropdown")
        
        for i, dropdown in enumerate(dropdown_groups):
            try:
                question_text = await extract_question_title(dropdown)
                if not question_text:
                    continue

                await dropdown.click()
                await page.wait_for_timeout(500)
                options_elems = await page.query_selector_all('div[role="option"]')
                options = []
                for option in options_elems:
                    if not await is_element_visible(option):
                        continue
                    option_text = await option.text_content()
                    if option_text and option_text.strip():
                        options.append(option_text.strip())

                await page.mouse.click(10, 10)

                if debug_mode:
                    logger.debug(f"Dropdown: {question_text.strip()} - Options: {options}")

                self.dropdown_groups.append({
                    'question': question_text.strip(),
                    'options': options,
                    'element': dropdown
                })
            except Exception as e:
                logger.error(f"Error saat menganalisis dropdown {i}: {str(e)}")
        
        # Tambahkan ke daftar pertanyaan
        self.questions = []
        
        # Text inputs
        for i, input_elem in enumerate(self.text_inputs):
            try:
                label_text = await extract_question_title(input_elem)
                if not label_text:
                    continue

                tag_name = await input_elem.evaluate("(el) => el.tagName.toLowerCase()")
                input_type = await input_elem.get_attribute('type') or 'text'
                if tag_name == 'textarea':
                    input_type = 'long_text'

                self.questions.append({
                    'type': input_type,
                    'question': label_text.strip(),
                    'element': input_elem
                })
            except Exception as e:
                logger.error(f"Error saat menganalisis input teks {i}: {str(e)}")
        
        # Radio groups
        for group in self.radio_groups:
            self.questions.append({
                'type': 'radio',
                'question': group['question'],
                'options': group['options'],
                'element': group['element']
            })
        
        # Checkbox groups
        for group in self.checkbox_groups:
            self.questions.append({
                'type': 'checkbox',
                'question': group['question'],
                'options': group['options'],
                'element': group['element']
            })
        
        # Dropdown groups
        for group in self.dropdown_groups:
            self.questions.append({
                'type': 'dropdown',
                'question': group['question'],
                'options': group['options'],
                'element': group['element']
            })

        # Fallback embedded-data hanya dipakai bila halaman aktif benar-benar tidak punya kontrol terdeteksi
        # dan halaman ini bukan intro/section kosong yang hanya punya tombol Berikutnya.
        if not self.questions and not (self.text_inputs or radio_groups or checkbox_groups or dropdown_groups):
            action_state = await detect_page_action_state(page)
            if action_state["has_next"] and not action_state["has_submit"]:
                logger.info("Halaman aktif tidak punya pertanyaan terlihat dan hanya menampilkan tombol Next; fallback embedded-data dilewati.")
            else:
                page_content = await safe_get_page_content(page)
                embedded_questions = self.extract_questions_from_embedded_data(page_content)
                if embedded_questions:
                    self.questions.extend(embedded_questions)
                    logger.info(f"Fallback embedded-data berhasil: {len(embedded_questions)} pertanyaan diekstrak")
        
        logger.info(f"Total {len(self.questions)} pertanyaan terdeteksi")

        if not self.questions:
            await self.save_analysis_debug(page, "no_questions_detected")
        
        # Save form structure to file for future use
        self.save_form_structure()
        
        return self.questions

    def extract_questions_from_embedded_data(self, page_content):
        """Ekstrak pertanyaan dari FB_PUBLIC_LOAD_DATA_ saat selector DOM tidak stabil."""
        try:
            match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.*?\]);</script>', page_content, re.DOTALL)
            if not match:
                return []

            data = json.loads(match.group(1))
            extracted = []
            seen = set()
            current_section = None

            def collect(node):
                nonlocal current_section
                if isinstance(node, list):
                    if self._looks_like_embedded_question(node):
                        if self._is_section_header(node):
                            current_section = (node[1] or "").strip()
                            if current_section and current_section not in self.sections:
                                self.sections.append(current_section)
                        question = self._parse_embedded_question(node)
                        if question and question['question'] not in seen:
                            if current_section:
                                question['section'] = current_section
                            extracted.append(question)
                            seen.add(question['question'])
                    for item in node:
                        collect(item)

            collect(data)
            return extracted
        except Exception as e:
            logger.error(f"Gagal ekstrak embedded form data: {str(e)}")
            return []

    def _looks_like_embedded_question(self, node):
        return (
            isinstance(node, list)
            and len(node) >= 4
            and isinstance(node[0], int)
            and isinstance(node[1], str)
            and isinstance(node[3], int)
        )

    def _is_section_header(self, node):
        return self._looks_like_embedded_question(node) and node[3] == 8

    def _parse_embedded_question(self, node):
        title = (node[1] or "").strip()
        qtype = node[3]

        # Abaikan section/header/deskripsi.
        if not title or qtype in {8}:
            return None

        options = []
        if len(node) > 4 and isinstance(node[4], list):
            for entry in node[4]:
                if isinstance(entry, list) and len(entry) > 1 and isinstance(entry[1], list):
                    for opt in entry[1]:
                        if isinstance(opt, list) and opt and isinstance(opt[0], str):
                            option_text = opt[0].strip()
                            if option_text:
                                options.append(option_text)

        if options:
            return {
                'type': 'radio',
                'question': title,
                'options': options,
            }

        # Fallback sederhana untuk isian teks.
        return {
            'type': 'text',
            'question': title,
        }

    async def save_analysis_debug(self, page, reason):
        """Simpan artefak debug saat analisis form gagal."""
        try:
            debug_dir = "analysis_debug"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_file = os.path.join(debug_dir, f"{reason}_{timestamp}.png")
            html_file = os.path.join(debug_dir, f"{reason}_{timestamp}.html")

            await page.screenshot(path=screenshot_file, full_page=True)
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(await safe_get_page_content(page))

            logger.warning(f"Artefak debug analisis disimpan: {screenshot_file}, {html_file}")
        except Exception as e:
            logger.error(f"Gagal menyimpan artefak debug analisis: {str(e)}")
    
    def save_form_structure(self):
        """Simpan struktur form untuk digunakan di masa depan"""
        try:
            # Buat struktur yang bisa di-serialize
            serializable_questions = []
            for q in self.questions:
                sq = {
                    'type': q['type'],
                    'question': q['question']
                }
                if 'options' in q:
                    sq['options'] = q['options']
                serializable_questions.append(sq)
            
            form_structure = {
                'url': FORM_URL,
                'language': self.language,
                'sections': self.sections,
                'questions': serializable_questions,
                'timestamp': datetime.now().isoformat()
            }
            
            # Buat nama file berdasarkan URL
            url_hash = abs(hash(FORM_URL)) % 10000
            structure_dir = "form_structures"
            if not os.path.exists(structure_dir):
                os.makedirs(structure_dir)
            
            structure_file = os.path.join(structure_dir, f"form_{url_hash}.json")
            
            with open(structure_file, 'w', encoding='utf-8') as f:
                json.dump(form_structure, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Struktur form disimpan ke: {structure_file}")
        except Exception as e:
            logger.error(f"Error saat menyimpan struktur form: {str(e)}")
    
    def load_form_structure(self, url):
        """Muat struktur form yang sebelumnya disimpan"""
        try:
            url_hash = abs(hash(url)) % 10000
            structure_file = os.path.join("form_structures", f"form_{url_hash}.json")
            
            if os.path.exists(structure_file):
                with open(structure_file, 'r', encoding='utf-8') as f:
                    structure = json.load(f)
                
                # Periksa apakah struktur masih valid (maksimal 1 hari)
                timestamp = datetime.fromisoformat(structure['timestamp'])
                if (datetime.now() - timestamp).days < 1 and structure['url'] == url and structure.get('questions'):
                    self.language = structure['language']
                    # Konversi kembali ke format internal
                    self.questions = structure['questions']
                    logger.info(f"Struktur form dimuat dari: {structure_file}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error saat memuat struktur form: {str(e)}")
            return False

    def generate_answer(self, question, response_context=None):
        """Menghasilkan jawaban acak berdasarkan jenis pertanyaan dengan peningkatan multi-bahasa"""
        question_text = question['question'].lower()
        response_context = response_context or {}

        def filter_free_text_options(options):
            blocked_markers = [
                "lainnya",
                "yang lain",
                "lain lain",
                "lain-lain",
                "other",
                "others",
                "prefer to self describe",
                "self describe",
            ]
            filtered = []
            for option in options:
                normalized_option = normalize_action_label(option)
                if any(marker in normalized_option for marker in blocked_markers):
                    continue
                filtered.append(option)
            return filtered
        
        if question['type'] in ['text', 'email', 'tel', 'number']:
            # Deteksi jenis teks yang diharapkan berdasarkan bahasa
            name_keywords = {
                'id': ['nama'],
                'en': ['name'],
                'es': ['nombre'],
                'fr': ['nom'],
                'de': ['name']
            }
            
            email_keywords = {
                'id': ['email', 'e-mail', 'surel'],
                'en': ['email', 'e-mail'],
                'es': ['email', 'correo'],
                'fr': ['email', 'courriel'],
                'de': ['email', 'e-mail']
            }
            
            phone_keywords = {
                'id': ['telepon', 'telp', 'hp', 'nomor'],
                'en': ['phone', 'mobile', 'cell'],
                'es': ['teléfono', 'móvil', 'celular'],
                'fr': ['téléphone', 'portable'],
                'de': ['telefon', 'handy']
            }
            
            address_keywords = {
                'id': ['alamat'],
                'en': ['address'],
                'es': ['dirección'],
                'fr': ['adresse'],
                'de': ['adresse']
            }
            
            # Deteksi berdasarkan tipe input
            if question['type'] == 'email':
                return fake.email()
            elif question['type'] == 'tel':
                return fake.phone_number()
            elif question['type'] == 'number':
                # Jika terkait umur
                if any(keyword in question_text for keyword in ['umur', 'usia', 'age', 'edad', 'âge', 'alter']):
                    return str(random.randint(18, 65))
                # Jika terkait tahun
                elif any(keyword in question_text for keyword in ['tahun', 'year', 'año', 'année', 'jahr']):
                    current_year = datetime.now().year
                    return str(random.randint(current_year - 10, current_year))
                # Default untuk angka
                return str(random.randint(1, 100))
            
            # Deteksi berdasarkan teks pertanyaan
            for lang, keywords in name_keywords.items():
                if any(keyword in question_text for keyword in keywords):
                    cached_name = response_context.get("generated_name")
                    if cached_name:
                        return cached_name

                    selected_gender = response_context.get("selected_gender")
                    generated_name = self._generate_gendered_name(selected_gender)
                    response_context["generated_name"] = generated_name
                    return generated_name
            
            for lang, keywords in email_keywords.items():
                if any(keyword in question_text for keyword in keywords):
                    return fake.email()
            
            for lang, keywords in phone_keywords.items():
                if any(keyword in question_text for keyword in keywords):
                    return fake.phone_number()
            
            for lang, keywords in address_keywords.items():
                if any(keyword in question_text for keyword in keywords):
                    return fake.address()
            
            # Deteksi lainnya
            if any(keyword in question_text for keyword in ['kota', 'city', 'ciudad', 'ville', 'stadt']):
                return fake.city()
            elif any(keyword in question_text for keyword in ['provinsi', 'province', 'provincia', 'état', 'bundesland']):
                return fake.state()
            elif any(keyword in question_text for keyword in ['kode pos', 'postal', 'zip', 'código postal', 'code postal', 'postleitzahl']):
                return fake.postcode()
            elif any(keyword in question_text for keyword in ['perusahaan', 'company', 'empresa', 'société', 'unternehmen']):
                return fake.company()
            elif any(keyword in question_text for keyword in ['pekerjaan', 'job', 'occupation', 'trabajo', 'métier', 'beruf']):
                return fake.job()
            else:
                # Jika tidak ada kecocokan khusus, berikan jawaban singkat
                return fake.sentence(nb_words=random.randint(3, 8))
        
        elif question['type'] == 'long_text':
            # Generate beberapa paragraf teks untuk area teks
            return fake.paragraph(nb_sentences=random.randint(3, 6))
                
        elif question['type'] == 'radio':
            if self._question_mentions_gender(question['question']):
                prepared_answer = response_context.get("gender_answer")
                if prepared_answer:
                    return prepared_answer

            # Pilih satu opsi acak
            valid_options = filter_free_text_options(question['options'])
            if len(valid_options) > 0:
                return random.choice(valid_options)
            if len(question['options']) > 0:
                return random.choice(question['options'])
            return None
        
        elif question['type'] == 'dropdown':
            if self._question_mentions_gender(question['question']):
                prepared_answer = response_context.get("gender_answer")
                if prepared_answer:
                    return prepared_answer

            # Pilih satu opsi acak, tapi hindari opsi pertama (biasanya "Pilih...")
            dropdown_options = question['options'][1:] if len(question['options']) > 1 else question['options']
            valid_options = filter_free_text_options(dropdown_options)
            if len(valid_options) > 0:
                return random.choice(valid_options)
            if len(dropdown_options) > 0:
                return random.choice(dropdown_options)
            return None
            
        elif question['type'] == 'checkbox':
            # Pilih 1-3 opsi acak (atau kurang jika tidak ada cukup opsi)
            valid_options = filter_free_text_options(question['options'])
            if len(valid_options) > 0:
                num_choices = min(random.randint(1, 3), len(valid_options))
                return random.sample(valid_options, num_choices)
            if len(question['options']) > 0:
                num_choices = min(random.randint(1, 3), len(question['options']))
                return random.sample(question['options'], num_choices)
            return []
            
        return None

async def fill_current_page_questions(page, form_analyzer, response_context=None, test_mode=False):
    """Isi semua pertanyaan yang terdeteksi pada halaman aktif."""
    if not form_analyzer.questions:
        return

    response_context = form_analyzer.prepare_response_context(form_analyzer.questions, response_context)

    for i, question in enumerate(form_analyzer.questions):
        logger.info(f"Mengisi pertanyaan {i+1}: {question['question'][:50]}{'...' if len(question['question']) > 50 else ''}")

        try:
            if 'element' in question:
                await question['element'].scroll_into_view_if_needed()
            await human_delay_short()
        except Exception:
            await natural_scroll_improved(page, 200)

        answer = form_analyzer.generate_answer(question, response_context=response_context)

        if test_mode:
            logger.debug(f"Jawaban yang akan dimasukkan: {answer}")
            if random.random() < 0.5:
                logger.debug("Melewati pertanyaan ini (mode pengujian)")
                continue

        if question['type'] == 'text':
            try:
                input_elem = question.get('element')
                if input_elem:
                    await human_type_into_element(page, input_elem, answer)
                else:
                    logger.warning(f"Tidak bisa menemukan input teks untuk pertanyaan {i+1}")
            except Exception as e:
                logger.error(f"Error saat mengisi teks: {str(e)}")

        elif question['type'] in ['email', 'tel', 'number']:
            try:
                input_elem = question.get('element')
                if input_elem:
                    await human_type_into_element(page, input_elem, answer)
                else:
                    logger.warning(f"Tidak bisa menemukan input {question['type']} untuk pertanyaan {i+1}")
            except Exception as e:
                logger.error(f"Error saat mengisi {question['type']}: {str(e)}")

        elif question['type'] == 'long_text':
            try:
                textarea = question.get('element')
                if textarea:
                    await human_type_into_element(page, textarea, answer)
                else:
                    logger.warning(f"Tidak bisa menemukan textarea untuk pertanyaan {i+1}")
            except Exception as e:
                logger.error(f"Error saat mengisi textarea: {str(e)}")

        elif question['type'] == 'radio':
            if answer:
                group_element = question.get('element')
                if group_element:
                    selected = await select_group_option(page, group_element, answer, "radio")
                    if not selected:
                        await human_select_option(page, answer)
                else:
                    await human_select_option(page, answer)

        elif question['type'] == 'dropdown':
            if answer:
                try:
                    if 'element' in question:
                        await human_click_improved(page, question['element'])
                        await human_delay_medium()

                        option_elements = await page.query_selector_all('div[role="option"]')
                        for option_elem in option_elements:
                            if not await is_element_visible(option_elem):
                                continue
                            option_text = (await option_elem.text_content() or "").strip()
                            if normalize_action_label(option_text) == normalize_action_label(answer.strip()):
                                await human_click_improved(page, option_elem)
                                break
                except Exception as e:
                    logger.error(f"Error saat memilih dropdown: {str(e)}")

        elif question['type'] == 'checkbox':
            for option in answer:
                group_element = question.get('element')
                if group_element:
                    selected = await select_group_option(page, group_element, option, "checkbox")
                    if not selected:
                        await human_select_option(page, option)
                else:
                    await human_select_option(page, option)
                await human_delay_medium()

        await human_delay_medium()

async def detect_submission_success(page):
    """Deteksi apakah form sudah benar-benar terkirim."""
    try:
        try:
            await page.wait_for_selector('div.freebirdFormviewerViewResponseConfirmationMessage', timeout=10000)
            return True
        except Exception:
            pass

        current_url = page.url
        if "formResponse" in current_url:
            return True

        page_content = await page.content()
        success_markers = [
            "Terima kasih",
            "Thank you",
            "telah dikirim",
            "response has been recorded",
        ]
        return any(marker in page_content for marker in success_markers)
    except Exception as e:
        logger.error(f"Error saat mendeteksi konfirmasi submit: {str(e)}")
        return False

async def fill_universal_form(page, form_analyzer, response_number, test_mode=False):
    """Mengisi formulir Google secara universal berdasarkan analisis struktur"""
    try:
        # Buka halaman form
        await page.goto(FORM_URL)
        await human_delay_medium()
        
        # Cek apakah ada captcha. Jangan lanjut bila challenge proteksi benar-benar muncul.
        if await detect_captcha(page):
            if test_mode:
                logger.warning("Captcha terdeteksi dalam mode pengujian. Menghentikan pengujian.")
            else:
                logger.warning("Captcha terdeteksi. Membatalkan proses saat ini.")
            return False
        
        page_number = 1
        response_context = {}
        repeated_signature_count = 0
        last_signature = None

        while True:
            current_signature = await get_page_signature(page)
            if current_signature == last_signature:
                repeated_signature_count += 1
            else:
                repeated_signature_count = 0
                last_signature = current_signature

            if repeated_signature_count >= 3:
                logger.error(f"Loop dihentikan karena halaman yang sama terdeteksi berulang kali di page counter {page_number}.")
                await form_analyzer.save_analysis_debug(page, "stuck_same_page")
                return False

            await form_analyzer.analyze_form(page, debug_mode=test_mode)

            if not form_analyzer.questions:
                logger.warning(f"Halaman {page_number} tidak memiliki pertanyaan terdeteksi.")
                action = await handle_next_or_submit(page)
                if action == "next":
                    page_number += 1
                    continue
                logger.error(f"Analisis form gagal di halaman {page_number}: 0 pertanyaan terdeteksi dan tidak ada tombol lanjut yang bisa dipakai.")
                return False

            await human_delay_medium()
            await natural_scroll_improved(page, 300, smooth=True)
            await fill_current_page_questions(page, form_analyzer, response_context=response_context, test_mode=test_mode)

            if test_mode:
                logger.info("Mode pengujian aktif: form tidak akan disubmit")
                test_dir = "test_results"
                if not os.path.exists(test_dir):
                    os.makedirs(test_dir)
                await page.screenshot(path=f"{test_dir}/test_form_filled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                return True

            await natural_scroll_improved(page, 300)
            await human_delay_long()

            action = await handle_next_or_submit(page)

            if action == "next":
                page_number += 1
                continue

            if action == "submit":
                success = await detect_submission_success(page)
                if success:
                    logger.info(f"Form ke-{response_number} berhasil diisi!")
                    return True

                logger.warning(f"Tidak yakin form ke-{response_number} berhasil terkirim.")
                return False

            logger.warning(f"Tidak menemukan tombol aksi valid di halaman {page_number}.")
            return False
    
    except Exception as e:
        logger.error(f"Error saat mengisi formulir ke-{response_number}: {str(e)}")
        # Screenshot untuk debugging
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(path=f"{screenshot_dir}/error-form-{response_number}-{timestamp}.png")
        return False

async def detect_captcha(page):
    """Deteksi adanya captcha di halaman"""
    try:
        captcha_selectors = [
            ('iframe[title*="recaptcha" i]', "recaptcha"),
            ('iframe[src*="recaptcha" i]', "recaptcha"),
            ('iframe[src*="hcaptcha" i]', "hcaptcha"),
            ('.g-recaptcha', "recaptcha"),
            ('[data-sitekey]', "captcha_widget"),
            ('textarea[name="g-recaptcha-response"]', "recaptcha"),
            ('textarea[name="h-captcha-response"]', "hcaptcha"),
            ('[aria-label*="captcha" i]', "captcha_ui"),
            ('[id*="captcha" i]', "captcha_ui"),
            ('[class*="captcha" i]', "captcha_ui"),
        ]

        for selector, label in captcha_selectors:
            element = await page.query_selector(selector)
            if element:
                logger.warning(f"Captcha terdeteksi via selector: {label} ({selector})")
                screenshot_dir = "captcha_screenshots"
                if not os.path.exists(screenshot_dir):
                    os.makedirs(screenshot_dir)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page.screenshot(path=f"{screenshot_dir}/{label}_{timestamp}.png")
                return True

        # Fallback teks dibuat lebih ketat agar tidak false positive pada kata umum seperti "verifikasi".
        visible_text = (await page.locator("body").inner_text()).lower()
        text_markers = [
            "i'm not a robot",
            "i am not a robot",
            "human verification",
            "security check",
            "complete the captcha",
            "enter the characters you see below",
            "recaptcha",
            "hcaptcha",
        ]
        if any(marker in visible_text for marker in text_markers):
            logger.warning("Captcha terdeteksi via teks yang sangat spesifik.")
            screenshot_dir = "captcha_screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"{screenshot_dir}/captcha_text_{timestamp}.png")
            return True

        return False
    except Exception as e:
        logger.error(f"Error saat mendeteksi captcha: {str(e)}")
        return False

# Tingkatkan perilaku manusia dengan pola ketik yang lebih realistis
async def human_type_improved(page, selector, text):
    """Ketik teks dengan pola manusia yang lebih realistis"""
    if isinstance(selector, str):
        await page.focus(selector)
    else:
        await selector.focus()
    await human_delay_short()  # Sedikit jeda sebelum mulai mengetik
    
    # Manusia sering mengetik dalam "burst" - kita akan mensimulasikan ini
    chunk_size = random.randint(2, 6)  # Ketik beberapa karakter sekaligus
    typing_speed_variations = [
        random.randint(MIN_TYPING_DELAY, MAX_TYPING_DELAY) for _ in range(len(text)//chunk_size + 1)
    ]
    
    i = 0
    while i < len(text):
        # Ambil chunk teks berikutnya
        end_index = min(i + random.randint(1, chunk_size), len(text))
        chunk = text[i:end_index]
        
        # Ketik chunk
        for char in chunk:
            await page.keyboard.type(char, delay=typing_speed_variations[i//chunk_size])
        
        # Kadang-kadang tambahkan jeda yang lebih lama (seperti berpikir atau teralihkan perhatian)
        if random.random() < 0.15:  # 15% kemungkinan
            # Jeda lebih lama setelah mengetik chunk
            await asyncio.sleep(random.randint(500, 2000) / 1000)
        
        # Kadang-kadang mensimulasikan kesalahan pengetikan dan koreksi
        if random.random() < 0.05 and i < len(text) - 1:  # 5% kemungkinan
            # Ketik karakter yang salah
            wrong_char = chr(ord(text[i]) + random.randint(1, 5))
            await page.keyboard.type(wrong_char, delay=typing_speed_variations[i//chunk_size])
            await asyncio.sleep(random.randint(300, 700) / 1000)  # Jeda saat menyadari kesalahan
            
            # Hapus kesalahan
            await page.keyboard.press("Backspace")
            await asyncio.sleep(random.randint(200, 500) / 1000)
            
            # Ketik karakter yang benar
            await page.keyboard.type(text[i], delay=typing_speed_variations[i//chunk_size])
        
        i = end_index
    
    # Kadang-kadang tambahkan jeda di akhir (seperti mengecek apa yang diketik)
    if random.random() < 0.2:  # 20% kemungkinan
        await asyncio.sleep(random.randint(500, 1500) / 1000)

async def natural_scroll_improved(page, distance, smooth=True):
    """Scroll dengan perilaku alami yang lebih realistis"""
    # Variasi jumlah langkah
    if smooth:
        steps = random.randint(5, 15)
    else:
        steps = random.randint(2, 5)  # Scroll lebih cepat
    
    # Variasi waktu antar scroll
    base_delay = random.randint(20, 50) if smooth else random.randint(10, 30)
    
    # Variasi kecepatan - manusia sering scroll lebih cepat di awal lalu melambat
    speeds = []
    for i in range(steps):
        if i < steps // 3:  # Awal: lebih cepat
            speeds.append(random.uniform(1.2, 1.5))
        elif i < 2 * steps // 3:  # Tengah: normal
            speeds.append(random.uniform(0.8, 1.2))
        else:  # Akhir: lebih lambat
            speeds.append(random.uniform(0.5, 0.8))
    
    # Manusia juga kadang scroll melebihi tujuan lalu kembali sedikit
    overshoot = random.random() < 0.3  # 30% kemungkinan
    
    for i in range(steps):
        step = (distance / steps) * speeds[i]
        await page.evaluate(f"window.scrollBy(0, {step})")
        delay = base_delay * (0.8 + random.random() * 0.4)  # Variasi ±20%
        await asyncio.sleep(delay / 1000)
    
    # Simulasi overshoot dan koreksi
    if overshoot:
        extra_scroll = random.uniform(30, 70)
        await page.evaluate(f"window.scrollBy(0, {extra_scroll})")
        await asyncio.sleep(random.randint(300, 700) / 1000)
        
        # Scroll back a bit
        await page.evaluate(f"window.scrollBy(0, {-extra_scroll * random.uniform(0.5, 0.8)})")
        await asyncio.sleep(random.randint(200, 400) / 1000)

async def human_click_improved(page, selector_or_element):
    """Klik elemen dengan pola manusia yang lebih realistis"""
    try:
        # Tentukan apakah input adalah selector atau element
        if isinstance(selector_or_element, str):
            element = await page.query_selector(selector_or_element)
            if not element:
                raise Exception(f"Elemen tidak ditemukan: {selector_or_element}")
        else:
            element = selector_or_element
        
        # Dapatkan bounding box
        box = await element.bounding_box()
        if not box:
            raise Exception(f"Tidak bisa mendapatkan posisi elemen")
        
        # Manusia biasanya tidak mengklik persis di tengah elemen
        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2
        
        # Tambahkan variasi dari tengah (gaussian distribution)
        target_x = center_x + random.gauss(0, box['width'] / 6)
        target_y = center_y + random.gauss(0, box['height'] / 6)
        
        # Pastikan tetap dalam batas elemen
        target_x = max(box['x'] + 2, min(box['x'] + box['width'] - 2, target_x))
        target_y = max(box['y'] + 2, min(box['y'] + box['height'] - 2, target_y))
        
        # Dapatkan posisi mouse saat ini
        mouse_position = await page.evaluate("() => { return {x: window.mousePosX || 0, y: window.mousePosY || 0} }")
        start_x = mouse_position['x']
        start_y = mouse_position['y']
        
        # Jika posisi awal tidak ada (pertama kali), buat sedikit di luar viewport
        if start_x == 0 and start_y == 0:
            viewport = page.viewport_size
            start_x = random.randint(-20, viewport['width'] + 20)
            start_y = random.randint(-20, viewport['height'] + 20)
        
        # Buat jalur mouse yang realistis (menggunakan kurva Bézier)
        points = 10  # Jumlah titik dalam jalur
        bezier_points = []
        
        # Control point untuk kurva Bézier
        control_x = start_x + (target_x - start_x) * random.uniform(0.3, 0.7)
        control_y = start_y + (target_y - start_y) * random.uniform(0.3, 0.7)
        
        # Kadang tambahkan variasi ke atas/bawah
        if random.random() < 0.5:
            control_y += random.uniform(-100, 100)
        else:
            control_x += random.uniform(-100, 100)
        
        # Hitung jalur Bézier
        for i in range(points):
            t = i / (points - 1)
            bx = (1 - t) * (1 - t) * start_x + 2 * (1 - t) * t * control_x + t * t * target_x
            by = (1 - t) * (1 - t) * start_y + 2 * (1 - t) * t * control_y + t * t * target_y
            bezier_points.append((bx, by))
        
        # Gerakkan mouse mengikuti jalur
        steps = len(bezier_points)
        for i, (x, y) in enumerate(bezier_points):
            # Variasi kecepatan - awal dan akhir lebih lambat
            if i < steps // 4 or i > 3 * steps // 4:
                delay_factor = random.uniform(1.0, 1.5)  # Lebih lambat
            else:
                delay_factor = random.uniform(0.7, 1.0)  # Lebih cepat
                
            await page.mouse.move(x, y)
            await asyncio.sleep(random.randint(5, 15) * delay_factor / 1000)
        
        # Kadang-kadang hover sebentar sebelum klik
        if random.random() < 0.3:  # 30% kemungkinan
            await asyncio.sleep(random.randint(100, 500) / 1000)
        
        # Variasi dalam jenis klik
        click_options = {}
        
        # Kadang-kadang klik lebih lama
        if random.random() < 0.2:  # 20% kemungkinan
            click_options["delay"] = random.randint(50, 150)
        
        # Klik
        await page.mouse.click(target_x, target_y, **click_options)
        
        # Kadang-kadang sedikit gerakkan mouse setelah klik
        if random.random() < 0.4:  # 40% kemungkinan
            await asyncio.sleep(random.randint(50, 200) / 1000)
            await page.mouse.move(
                target_x + random.uniform(-20, 20), 
                target_y + random.uniform(-20, 20)
            )
        
        return True
    except Exception as e:
        logger.error(f"Error saat mengklik elemen: {str(e)}")
        return False

async def human_type_into_element(page, element, text):
    """Ketik ke element handle spesifik agar tidak salah mengisi field lain."""
    try:
        await element.scroll_into_view_if_needed()
        await human_click_improved(page, element)
        await human_delay_short()
        try:
            await element.fill("")
        except Exception:
            pass
        await human_type_improved(page, element, text)
        return True
    except Exception as e:
        logger.error(f"Error saat mengetik ke elemen spesifik: {str(e)}")
        return False

async def select_group_option(page, group_element, choice_text, role):
    """Pilih opsi dalam grup radio/checkbox tertentu, bukan global satu halaman."""
    try:
        selector = f'div[role="{role}"]'
        options = await group_element.query_selector_all(selector)
        normalized_choice = normalize_action_label(choice_text)

        for option in options:
            if not await is_element_visible(option):
                continue

            option_text = await extract_option_label(option)
            normalized_option = normalize_action_label(option_text)
            logger.debug(f"Opsi {role} kandidat: {normalized_option}")
            if (
                normalized_option == normalized_choice
                or normalized_choice in normalized_option
                or normalized_option in normalized_choice
            ):
                await option.scroll_into_view_if_needed()
                await human_click_improved(page, option)
                await human_delay_short()

                checked = (await option.get_attribute("aria-checked") or "").lower()
                if checked == "true":
                    return True

                try:
                    await option.click(force=True)
                    await human_delay_short()
                except Exception:
                    pass

                checked = (await option.get_attribute("aria-checked") or "").lower()
                if checked == "true":
                    return True

                logger.warning(f"Opsi '{choice_text}' ditemukan tetapi tidak berubah menjadi terpilih.")
                return False

        logger.warning(f"Tidak bisa menemukan opsi '{choice_text}' dalam grup {role}.")
        return False
    except Exception as e:
        logger.error(f"Error saat memilih opsi '{choice_text}' di grup {role}: {str(e)}")
        return False

async def main():
    print(f"\n{'='*70}")
    print(f"{'PENGISI OTOMATIS GOOGLE FORM UNIVERSAL':^70}")
    print(f"{'='*70}\n")
    
    # Buat mode pengujian
    test_mode = "--test" in sys.argv
    if test_mode:
        logger.info("MODE PENGUJIAN AKTIF - Form akan diisi tetapi tidak akan disubmit")
        
        # Buat direktori untuk hasil pengujian
        test_dir = "test_results"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
    
    # Tampilkan informasi konfigurasi
    print(f"Akan mengisi {TOTAL_RESPONSES} respons ke Google Form")
    print(f"URL Form: {FORM_URL}")
    print(f"Dibagi menjadi {(TOTAL_RESPONSES + MAX_PER_SESSION - 1) // MAX_PER_SESSION} sesi")
    print(f"Mode headless: {HEADLESS_MODE}")
    if PROXIES:
        print(f"Menggunakan {len(PROXIES)} proxy")
    
    # Pengecekan proxy
    if PROXIES and test_mode:
        logger.info("Menguji proxy...")
        async with async_playwright() as p:
            for i, proxy in enumerate(PROXIES[:min(3, len(PROXIES))]):
                try:
                    browser = await p.chromium.launch(proxy={"server": proxy})
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto("https://api.ipify.org?format=json", timeout=10000)
                    content = await page.content()
                    logger.info(f"Proxy {i+1} berhasil: {content}")
                    await browser.close()
                except Exception as e:
                    logger.error(f"Proxy {i+1} gagal: {str(e)}")
    
    print(f"\nCatatan: Gunakan alat ini hanya untuk tujuan pendidikan dan dengan izin pemilik formulir.")
    print(f"{'='*70}\n")
    
    confirm = input("Apakah Anda yakin ingin melanjutkan? (y/n): ").lower()
    if confirm != 'y':
        print("Program dibatalkan.")
        return
    
    print("\nMemulai proses pengisian formulir...")
    
    total_success = 0
    start_time_total = time.time()
    form_analyzer = FormAnalyzer()
    
    # Bagi pengisian menjadi beberapa sesi untuk menghindari deteksi
    sessions_needed = (TOTAL_RESPONSES + MAX_PER_SESSION - 1) // MAX_PER_SESSION
    
    for session in range(sessions_needed):
        logger.info(f"\n{'='*70}")
        logger.info(f" SESI {session+1} DARI {sessions_needed} ".center(70, "="))
        logger.info(f"{'='*70}\n")
        
        session_start = session * MAX_PER_SESSION + 1
        session_end = min((session + 1) * MAX_PER_SESSION, TOTAL_RESPONSES)
        session_count = session_end - session_start + 1
        
        logger.info(f"Mengisi {session_count} formulir dalam sesi ini ({session_start}-{session_end})")
        
        # Pilih proxy untuk sesi ini jika tersedia
        current_proxy = None
        if PROXIES:
            current_proxy = random.choice(PROXIES)
            logger.info(f"Menggunakan proxy: {current_proxy}")
        
        async with async_playwright() as p:
            # Gunakan user-agent acak
            user_agent = random.choice(USER_AGENTS)
            
            # Konfigurasi browser
            browser_args = {
                "headless": HEADLESS_MODE,
            }
            
            # Tambahkan proxy jika tersedia
            if current_proxy:
                browser_args["proxy"] = {
                    "server": current_proxy
                }
            
            # Buat konteks browser dengan viewport dan user-agent acak
            browser = await p.chromium.launch(**browser_args)
            context = await browser.new_context(
                viewport={
                    "width": random.choice([1280, 1366, 1440, 1920]),
                    "height": random.choice([720, 768, 900, 1080])
                },
                user_agent=user_agent
            )
            
            # Acak ukuran jendela sedikit untuk variasi
            page = await context.new_page()
            
            session_success = 0
            session_start_time = time.time()
            
            try:
                for i in range(session_start, session_end + 1):
                    logger.info(f"\nMengisi formulir ke-{i} dari {TOTAL_RESPONSES} (Sesi {session+1})...")
                    
                    # Coba isi formulir
                    result = await fill_universal_form(page, form_analyzer, i, test_mode=test_mode)
                    if result:
                        session_success += 1
                        total_success += 1
                        
                        # Dalam mode pengujian, cukup satu form saja
                        if test_mode:
                            logger.info("Pengujian berhasil! Menghentikan pengujian setelah 1 form.")
                            break
                    elif not form_analyzer.questions:
                        logger.error("Menghentikan sesi karena analisis form tidak berhasil.")
                        break
                    
                    # Tampilkan kemajuan
                    forms_completed = i - session_start + 1
                    elapsed_time = time.time() - session_start_time
                    
                    if forms_completed > 0:
                        estimated_session_time = (elapsed_time / forms_completed) * session_count
                        remaining_session_time = estimated_session_time - elapsed_time
                        
                        logger.info(f"Kemajuan sesi: {forms_completed}/{session_count} ({forms_completed/session_count*100:.1f}%)")
                        logger.info(f"Waktu sesi berlalu: {elapsed_time/60:.1f} menit")
                        logger.info(f"Perkiraan waktu tersisa sesi ini: {remaining_session_time/60:.1f} menit")
                    
                    # Variasi jeda antar pengisian (1.5-3 menit)
                    if i < session_end and not test_mode and form_analyzer.questions:
                        wait_time = random.uniform(90, 180)  # 1.5-3 menit
                        logger.info(f"Menunggu {wait_time:.1f} detik sebelum mengisi formulir berikutnya...")
                        await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"\nTerjadi kesalahan dalam sesi {session+1}: {str(e)}")
            finally:
                await browser.close()
                
                # Tampilkan ringkasan sesi
                logger.info("\n" + "="*70)
                logger.info(f" RINGKASAN SESI {session+1} ".center(70, "="))
                logger.info("="*70)
                logger.info(f"Total formulir berhasil dalam sesi ini: {session_success} dari {session_count}")
                logger.info(f"Total waktu sesi: {(time.time() - session_start_time)/60:.1f} menit")
                logger.info("="*70)
        
        # Dalam mode pengujian, hentikan setelah sesi pertama
        if test_mode:
            break
        
        # Jeda antar sesi (kecuali sesi terakhir)
        if session < sessions_needed - 1:
            session_pause = random.randint(MIN_SESSION_PAUSE, MAX_SESSION_PAUSE)
            next_session_time = datetime.now().timestamp() + session_pause
            next_session_str = datetime.fromtimestamp(next_session_time).strftime("%H:%M:%S")
            
            logger.info(f"\nJeda selama {session_pause//60} menit untuk menghindari deteksi.")
            logger.info(f"Sesi berikutnya akan dimulai pada: {next_session_str}")
            
            # Countdown timer
            for i in range(session_pause, 0, -60):
                minutes_left = i // 60
                print(f"\rMenunggu sesi berikutnya. Waktu tersisa: {minutes_left} menit...", end="")
                await asyncio.sleep(60)
            
            print("\rSiap memulai sesi berikutnya!                               ")
    
    # Tampilkan ringkasan total
    total_time = time.time() - start_time_total
    logger.info("\n" + "="*70)
    logger.info(" RINGKASAN PENGISIAN TOTAL ".center(70, "="))
    logger.info("="*70)
    logger.info(f"Total formulir berhasil diisi: {total_success} dari {TOTAL_RESPONSES}")
    logger.info(f"Total waktu: {total_time/60:.1f} menit ({total_time/3600:.2f} jam)")
    if total_success > 0:
        logger.info(f"Rata-rata waktu per formulir: {total_time/total_success:.1f} detik")
    logger.info("="*70)

if __name__ == "__main__":
    asyncio.run(main())
