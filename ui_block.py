"""Theme controls and responsive iMessage-inspired styling for the Streamlit chat."""

import streamlit as st

ACCENTS = {
    "ฟ้า": "#0071E3",
    "เขียว": "#248A3D",
    "ม่วง": "#8944AB",
    "ชมพู": "#D30F45",
    "ส้ม": "#C93400",
}
THEMES = ["อัตโนมัติ", "สว่าง", "มืด"]
LAYOUTS = ["📱 มือถือ", "🖥️ คอมพิวเตอร์"]


def initialize_ui():
    st.session_state.setdefault("ui_theme", THEMES[0])
    st.session_state.setdefault("ui_accent", "ฟ้า")
    # Keep existing preferences from older versions while giving new desktop
    # sessions a layout that matches the computer they're using.
    old_layouts = {"📱 แบบ iPhone": LAYOUTS[0], "🖥️ เต็มจอ": LAYOUTS[1]}
    current_layout = st.session_state.get("ui_layout", LAYOUTS[1])
    st.session_state["ui_layout"] = old_layouts.get(current_layout, current_layout)
    if st.session_state["ui_layout"] not in LAYOUTS:
        st.session_state["ui_layout"] = LAYOUTS[1]


def add_appearance_controls():
    """Render appearance controls in the open sidebar."""
    st.markdown("#### 🎨 ปรับหน้าตา")
    st.radio("อุปกรณ์ที่ใช้", LAYOUTS, key="ui_layout", horizontal=True)
    st.caption("บนคอม เลือก ‘มือถือ’ เพื่อดูตัวอย่างในกรอบโทรศัพท์ได้ ส่วนมือถือจริงจะจัดหน้าให้พอดีหน้าจออัตโนมัติ")
    st.radio("ธีม", THEMES, key="ui_theme", horizontal=True)
    st.selectbox("สีหลัก", list(ACCENTS), key="ui_accent")
    st.caption("สีพื้นหลังจะปรับให้เข้ากับสีหลักโดยอัตโนมัติ")


def build_css(theme, accent, layout):
    light_backgrounds = {
        ACCENTS["ฟ้า"]: "#F2F7FD",
        ACCENTS["เขียว"]: "#F3F8F3",
        ACCENTS["ม่วง"]: "#F7F4FA",
        ACCENTS["ชมพู"]: "#FDF4F6",
        ACCENTS["ส้ม"]: "#FCF6F1",
    }
    dark_desks = {
        ACCENTS["ฟ้า"]: "#0D1420",
        ACCENTS["เขียว"]: "#0D160F",
        ACCENTS["ม่วง"]: "#15101B",
        ACCENTS["ชมพู"]: "#190E13",
        ACCENTS["ส้ม"]: "#19120D",
    }
    page_background = light_backgrounds.get(accent, light_backgrounds[ACCENTS["ฟ้า"]])
    desk_background = dark_desks.get(accent, dark_desks[ACCENTS["ฟ้า"]])
    light = (
        f"--bg:{page_background}; --surface:#FFFFFF; --bubble-in:#E8E8ED; "
        "--text:#1D1D1F; --muted:#6E6E73; --border:rgba(0,0,0,.12); "
        f"--nav:rgba(245,245,247,.88); --desk:{page_background};"
    )
    dark = (
        f"--bg:{desk_background}; "
        f"--surface:color-mix(in srgb, {desk_background} 78%, #29364A); "
        f"--bubble-in:color-mix(in srgb, {desk_background} 66%, #354156); "
        "--text:#F5F7FA; --muted:#A7B0C0; --border:rgba(255,255,255,.14); "
        f"--nav:color-mix(in srgb, {desk_background} 88%, transparent); --desk:{desk_background};"
    )

    if theme == "มืด":
        theme_css = f":root {{ color-scheme: dark; {dark} }}"
    elif theme == "สว่าง":
        theme_css = f":root {{ color-scheme: light; {light} }}"
    else:
        theme_css = (
            f":root {{ color-scheme: light dark; {light} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root {{ {dark} }} }}"
        )

    if layout == LAYOUTS[0]:
        desktop_css = """
@media (min-width: 900px) {
  :root { --phone-height: min(860px, calc(100vh - 48px)); }
  .stApp { background: var(--desk); }
  .block-container {
    width: 430px; max-width: calc(100vw - 40px); height: var(--phone-height);
    min-height: 0; max-height: var(--phone-height); box-sizing: border-box;
    margin: calc((100vh - var(--phone-height)) / 2) auto 0; overflow-y: auto;
    overscroll-behavior: contain; background: var(--bg); border: 11px solid #1C1C1E;
    border-bottom: none; border-radius: 54px 54px 0 0; padding: 14px 16px 9rem !important;
  }
  [data-testid="stBottom"] {
    bottom: calc((100vh - var(--phone-height)) / 2); z-index: 20;
    background: transparent !important; backdrop-filter: none !important;
  }
  [data-testid="stBottomBlockContainer"] {
    width: 430px; max-width: calc(100vw - 40px); box-sizing: border-box;
    margin: 0 auto; background: transparent !important;
    backdrop-filter: none; -webkit-backdrop-filter: none;
    border: 11px solid #1C1C1E; border-top: none;
    border-radius: 0 0 54px 54px; padding: 4px 14px 12px !important;
  }
  .ios-status {
    display: flex; position: sticky; top: 0; z-index: 50;
    background: var(--bg); margin: 0 -1px;
  }
  .ios-island { display: block; position: sticky; top: 0; z-index: 51; }
  [data-testid="stChatMessageContent"] { max-width: 80% !important; }
}
"""
    else:
        desktop_css = """
@media (min-width: 900px) {
  .stApp { background: var(--desk); }
  .block-container { max-width: 1040px; padding: 1.25rem 2rem 9rem !important; }
  .app-topbar {
    flex-direction: row; text-align: left; justify-content: flex-start; gap: 12px;
    margin: 0 0 20px; padding: 12px 16px; border: 1px solid var(--border);
    border-radius: 18px; background: var(--nav); backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px); box-shadow: 0 4px 18px rgba(0,0,0,.035);
  }
  .app-avatar { width: 46px; height: 46px; flex: 0 0 46px; font-size: 23px; }
  .app-title { margin-left: 0; }
  [data-testid="stBottomBlockContainer"] {
    max-width: 1040px; margin: 0 auto; padding: 12px 24px 18px !important;
    background: transparent !important; border: 0 !important;
  }
  [data-testid="stChatMessageContent"] { max-width: 72% !important; }
  .welcome { padding: 44px 36px 38px; }
}
"""

    css = """
<style>
__THEME__
:root { --accent: __ACCENT__; }
html, body, [class*="css"], .stApp {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Noto Sans Thai", "Leelawadee UI", "Segoe UI", Tahoma, sans-serif;
}
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; height: 0; }
.block-container { max-width: 760px; padding: 1rem 1.25rem 9rem; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
.stApp label { color: var(--text); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
}

/* iPhone status area, shown only in desktop iPhone preview */
.ios-status {
  display: none; justify-content: space-between; align-items: center;
  padding: 2px 18px 0; font-size: 15px; font-weight: 600; color: var(--text); height: 30px;
}
.ios-status .icons { display: flex; gap: 6px; align-items: center; font-size: 12px; letter-spacing: 1px; }
.ios-battery { width: 24px; height: 12px; border: 1.5px solid var(--text); border-radius: 4px; padding: 1px; opacity: .9; }
.ios-battery i { display: block; height: 100%; width: 80%; background: var(--text); border-radius: 2px; }
.ios-island { display: none; width: 112px; height: 32px; background: #000; border-radius: 20px; margin: -30px auto 6px; }

/* iMessage-inspired header */
.app-topbar {
  display: flex; flex-direction: column; align-items: center; text-align: center; gap: 6px;
  padding: 10px 0 14px; border-bottom: 1px solid var(--border); margin: 0 -4px 14px;
}
.app-avatar {
  display: flex; align-items: center; justify-content: center; width: 56px; height: 56px;
  border-radius: 50%; background: var(--accent); color: #fff; font-size: 28px;
}
.app-name { font-size: 15px; font-weight: 600; color: var(--text); letter-spacing: -.2px; }
.app-name span { color: var(--muted); font-weight: 400; }
.app-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
.app-sub b { color: #34C759; font-weight: 700; }
.app-title { min-width: 0; }
.app-provider {
  display: inline-flex; align-items: center; gap: 5px; width: fit-content; margin-top: 6px;
  padding: 3px 9px 3px 6px; border: 1px solid var(--border); border-radius: 999px;
  background: var(--surface); color: var(--muted); font-size: 11px; line-height: 1.35;
  text-decoration: none !important; transition: border-color .16s ease, box-shadow .16s ease;
}
.app-provider img { display: block; width: 15px; height: 15px; object-fit: contain; }
.app-provider:hover { color: var(--text); border-color: color-mix(in srgb, var(--accent) 50%, var(--border)); box-shadow: 0 2px 10px color-mix(in srgb, var(--accent) 12%, transparent); }
.chat-date { text-align: center; font-size: 12px; color: var(--muted); margin: 4px 0 10px; }
.chat-date b { font-weight: 600; }

/* Welcome screen */
.welcome {
  max-width: 680px; margin: 30px auto 20px; padding: 30px 28px 26px; text-align: center;
  background: var(--surface); border: 1px solid var(--border); border-radius: 24px;
  box-shadow: 0 8px 28px rgba(0,0,0,.045);
}
.welcome-icon {
  width: 64px; height: 64px; margin: 0 auto 16px; border-radius: 18px; display: flex;
  align-items: center; justify-content: center; font-size: 32px;
  background: color-mix(in srgb, var(--accent) 9%, var(--surface));
  border: 1px solid color-mix(in srgb, var(--accent) 18%, var(--border));
  box-shadow: 0 8px 22px color-mix(in srgb, var(--accent) 11%, transparent);
}
.welcome-title { font-size: clamp(25px, 4vw, 32px); line-height: 1.25; font-weight: 700; letter-spacing: -.5px; color: var(--text); margin: 0 0 8px; }
.welcome-copy { margin: 0 auto; max-width: 340px; color: var(--muted); font-size: 15px; line-height: 1.6; }
.starter-heading {
  display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
  max-width: 900px; margin: 4px auto 10px; padding: 0 2px;
  color: var(--text); font-size: 14px; font-weight: 650; letter-spacing: -.1px;
}
.starter-hint { color: var(--muted); font-size: 12px; font-weight: 400; }

/* Chat bubbles */
[data-testid="stChatMessage"] {
  background: transparent !important; border: none !important; box-shadow: none !important;
  display: flex !important; flex-flow: row nowrap !important; justify-content: flex-start !important;
  align-items: flex-end !important; gap: 8px !important; width: 100% !important;
  padding: 2px 0 !important; margin: 0 0 8px !important;
}
[data-testid="stChatMessage"] > div:has([data-testid="stChatMessageAvatarAssistant"]) {
  flex: 0 0 30px !important; width: 30px !important; min-width: 30px !important;
  margin: 0 !important; align-self: flex-end !important;
}
[data-testid="stChatMessageContent"] {
  display: block !important; flex: 0 1 auto !important; align-self: flex-end !important;
  width: fit-content !important; max-width: min(82%, 760px) !important;
  min-width: 0 !important; min-height: 0 !important; height: auto !important; overflow: visible !important;
  margin: 0 !important; background: var(--bubble-in); color: var(--text); padding: 10px 14px !important;
  border-radius: 20px 20px 20px 6px;
}
[data-testid="stChatMessageAvatarAssistant"] {
  flex: 0 0 30px !important; align-self: flex-end !important; margin: 0 !important;
}
[data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarUser"])) [data-testid="stChatMessageContent"] {
  margin: 0 auto 0 0 !important;
}
[data-testid="stChatMessageContent"] > div,
[data-testid="stChatMessageContent"] .stVerticalBlock,
[data-testid="stChatMessageContent"] [data-testid="stElementContainer"] {
  width: fit-content !important; max-width: 100% !important;
}
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] {
  min-width: 0; margin: 0 !important; overflow-wrap: anywhere;
}
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] p {
  font-size: 16px; line-height: 1.5; color: inherit; margin: 0 0 .35rem !important;
}
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] img { border-radius: 14px; max-width: 100%; }
[data-testid="stChatMessageAvatarAssistant"] { width: 30px; height: 30px; border-radius: 50%; background: var(--accent); color: #fff; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  justify-content: flex-end !important;
}
[data-testid="stChatMessageAvatarUser"] { display: none !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div:has([data-testid="stChatMessageAvatarUser"]) {
  display: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  align-self: flex-end !important; width: fit-content !important;
  max-width: min(82%, 760px) !important; background: var(--accent); color: #fff;
  border-radius: 20px 20px 6px 20px; margin: 0 0 0 auto !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] p { color: #fff !important; }
[data-testid="stChatMessageContent"] [data-testid="stExpander"] details {
  border: none; background: color-mix(in srgb, var(--surface) 70%, transparent); border-radius: 12px;
}
[data-testid="stChatMessageContent"] [data-testid="stExpander"] summary { font-size: 13px; color: var(--accent); }
[data-testid="stChatMessageContent"] a { color: var(--accent); }
[data-testid="stSpinner"] i { border-color: var(--accent) transparent transparent !important; }
.typing-indicator { display: flex; align-items: center; gap: 10px; min-height: 26px; }
[data-testid="stChatMessageContent"]:has(.typing-indicator) {
  align-self: flex-end !important; margin: 0 auto 0 0 !important; width: fit-content !important;
  max-width: min(82%, 760px) !important;
}
.typing-dots { display: inline-flex; align-items: center; gap: 4px; height: 12px; }
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
  animation: typing-bounce 1.15s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: .14s; }
.typing-dots span:nth-child(3) { animation-delay: .28s; }
.typing-label { color: var(--muted); font-size: 14px; line-height: 1.4; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: .5; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* Composer */
[data-testid="stBottom"] { background: var(--nav) !important; backdrop-filter: blur(16px) !important; -webkit-backdrop-filter: blur(16px) !important; border-top: 1px solid var(--border); }
[data-testid="stBottom"]::before, [data-testid="stBottom"]::after { background: var(--bg) !important; }
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: transparent !important; }
[data-testid="stChatInput"] { border: 1px solid var(--border) !important; border-radius: 980px !important; background: var(--surface) !important; box-shadow: 0 2px 10px rgba(0,0,0,.035) !important; }
[data-testid="stChatInput"] > div { background: transparent !important; border: none !important; }
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] { background: transparent !important; border: 0 !important; box-shadow: none !important; }
[data-testid="stChatInput"] textarea {
  font-size: 16px; color: var(--text) !important; background: transparent !important;
  border: 0 !important; box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; opacity: 1; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent) !important; }
[data-testid="stChatInputSubmitButton"] { background: var(--accent) !important; color: #fff !important; border-radius: 50% !important; }
[data-testid="stChatInputSubmitButton"] svg { fill: #fff !important; color: #fff !important; }

/* Bento-inspired question cards: a quiet edge highlight appears on hover. */
.stButton button {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  width: 100%; min-height: 66px; padding: 12px 16px; border-radius: 18px;
  border: 1px solid var(--border); background: var(--surface); color: var(--text); text-align: left;
  box-shadow: 0 2px 10px rgba(0,0,0,.025);
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, background-color .16s ease;
}
.stButton button > div { flex: 1 1 auto; min-width: 0; text-align: left; }
.stButton button p {
  width: 100%; margin: 0 !important; color: var(--text) !important; text-align: left; line-height: 1.4; font-weight: 550;
}
.stButton button::after {
  content: "↗"; flex: 0 0 auto; width: 24px; height: 24px; display: grid; place-items: center;
  border-radius: 50%; background: color-mix(in srgb, var(--accent) 9%, var(--surface));
  color: var(--accent); font-size: 13px; line-height: 1;
}
.stButton button:hover {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--border));
  background: color-mix(in srgb, var(--accent) 2.5%, var(--surface));
  box-shadow: 0 8px 22px color-mix(in srgb, var(--accent) 9%, transparent);
  transform: translateY(-1px);
}
.stButton button:active { transform: scale(.985); }
[data-testid="stSidebar"] .stButton button {
  min-height: 46px; border-radius: 980px; border: 1px solid var(--border);
  padding: 9px 14px; background: var(--surface); color: var(--text);
}
[data-testid="stSidebar"] .stButton button p { color: var(--text) !important; text-align: center; }
[data-testid="stSidebar"] .stButton button::after { content: none; }
button:focus-visible, a:focus-visible, textarea:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }
[data-testid="stSidebar"] { background: var(--surface); border-right: .5px solid var(--border); }
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: var(--surface) !important; color: var(--text) !important; border-color: var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] input { color: var(--text) !important; }
[data-testid="stSidebar"] input[type="radio"], [data-testid="stSidebar"] input[type="checkbox"] { accent-color: var(--accent) !important; }
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { border-color: var(--border) !important; }
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child {
  background: transparent !important; border-color: var(--accent) !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) > div:first-child > div {
  background: var(--accent) !important; border-color: var(--accent) !important;
}
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] summary { color: var(--text) !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
[data-testid="stExpander"] details { border-color: var(--border); border-radius: 12px; }

@media (max-width: 640px) {
  .block-container { padding: calc(4rem + env(safe-area-inset-top)) .75rem calc(7rem + env(safe-area-inset-bottom)) !important; }
  .app-topbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    flex-direction: row; justify-content: flex-start; text-align: left; gap: 10px;
    margin: 0; padding: calc(8px + env(safe-area-inset-top)) 16px 10px;
    background: var(--nav); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border); box-shadow: 0 4px 16px rgba(0,0,0,.045);
  }
  .app-avatar { width: 42px; height: 42px; flex: 0 0 42px; font-size: 21px; }
  .app-name { font-size: 15px; }
  .app-sub { font-size: 12px; }
  .app-provider { margin-top: 4px; }
  .welcome { margin: 20px auto 12px; padding: 24px 18px 20px; }
  .starter-heading { align-items: flex-start; font-size: 13px; }
  .starter-hint { font-size: 11px; text-align: right; }
  .stButton button { min-height: 58px; padding: 10px 12px; border-radius: 16px; }
  [data-testid="stChatMessageContent"] { max-width: min(82%, 760px) !important; }
  [data-testid="stBottom"] {
    background: var(--nav) !important; padding-bottom: env(safe-area-inset-bottom) !important;
  }
  [data-testid="stBottomBlockContainer"] {
    padding: 8px 12px calc(10px + env(safe-area-inset-bottom)) !important;
    background: transparent !important;
  }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; }
}
__DESKTOP__
</style>
"""
    return css.replace("__THEME__", theme_css).replace("__ACCENT__", accent).replace("__DESKTOP__", desktop_css)

