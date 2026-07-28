"""
Shared visual theme for VoiceAttendAI -- indigo/purple palette matching
the reference dashboard mockup.

Import and call apply_theme() at the top of every page, right after
st.set_page_config(), then use page_header() / section_label() /
metric_card() / quick_action() as needed.
"""

import streamlit as st


PRIMARY = "#6D5DF6"       # indigo/purple
PRIMARY_DARK = "#4C3FD7"
TEXT = "#1F2333"
TEXT_MUTED = "#6B7280"
BORDER = "#E7E5F5"
BG_SOFT = "#F6F5FC"

GREEN = "#22C55E"
GREEN_BG = "#E9FBEF"
RED = "#EF4444"
RED_BG = "#FDECEC"
BLUE = "#3B82F6"
BLUE_BG = "#EAF1FE"
PURPLE_BG = "#F1EEFE"
ORANGE = "#F59E0B"
ORANGE_BG = "#FEF6E7"


def apply_theme():
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}

            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}

            /* force light theme everywhere so nothing goes invisible
               if the browser/OS is set to dark mode */
            .stApp {{
                background-color: #FFFFFF !important;
            }}
            .stApp, .stApp p, .stApp li, .stApp span, .stApp label,
            .stApp div, .stMarkdown, .stText {{
                color: {TEXT} !important;
            }}
            .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
                color: {TEXT} !important;
            }}

            /* ---------------- page header ---------------- */
            .vai-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding-bottom: 16px;
                margin-bottom: 20px;
                border-bottom: 1px solid {BORDER};
            }}
            .vai-header .left {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .vai-header .icon {{
                width: 46px;
                height: 46px;
                border-radius: 12px;
                background: {PRIMARY};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
            }}
            .vai-header .titles h1 {{
                font-size: 22px;
                font-weight: 800;
                margin: 0;
                padding: 0;
            }}
            .vai-header .titles p {{
                font-size: 13px;
                color: {TEXT_MUTED} !important;
                margin: 2px 0 0 0;
            }}

            /* ---------------- generic card ---------------- */
            .vai-card {{
                background: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 14px;
                padding: 18px 20px;
                margin-bottom: 16px;
                box-shadow: 0 2px 8px rgba(109, 93, 246, 0.06);
            }}
            .vai-card h3 {{
                margin-top: 0;
                font-size: 16px;
                font-weight: 700;
            }}

            .vai-section-label {{
                text-transform: uppercase;
                letter-spacing: 0.06em;
                font-size: 12px;
                font-weight: 700;
                color: {PRIMARY} !important;
                margin-bottom: 8px;
            }}

            /* ---------------- metric stat card ---------------- */
            .vai-stat {{
                background: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 14px;
                padding: 16px 18px;
                box-shadow: 0 2px 8px rgba(109, 93, 246, 0.06);
                position: relative;
                overflow: hidden;
            }}
            .vai-stat .stat-icon {{
                width: 38px;
                height: 38px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                margin-bottom: 10px;
            }}
            .vai-stat .stat-label {{
                font-size: 13px;
                color: {TEXT_MUTED} !important;
                font-weight: 600;
            }}
            .vai-stat .stat-value {{
                font-size: 28px;
                font-weight: 800;
                margin: 2px 0 2px 0;
            }}
            .vai-stat .stat-sub {{
                font-size: 12px;
                color: {TEXT_MUTED} !important;
            }}
            .vai-stat .stat-bar {{
                height: 4px;
                border-radius: 4px;
                margin-top: 10px;
            }}

            /* ---------------- quick action tile ---------------- */
            .vai-action {{
                display: flex;
                align-items: center;
                gap: 12px;
                border-radius: 12px;
                padding: 14px 16px;
                border: 1px solid {BORDER};
                margin-bottom: 12px;
            }}
            .vai-action .a-icon {{
                width: 36px;
                height: 36px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 17px;
                flex-shrink: 0;
            }}
            .vai-action .a-title {{
                font-weight: 700;
                font-size: 14px;
                margin: 0;
            }}
            .vai-action .a-sub {{
                font-size: 12px;
                color: {TEXT_MUTED} !important;
                margin: 0;
            }}

            /* streamlit page_link styled as a plain nav row */
            [data-testid="stPageLink"] {{
                border-radius: 8px !important;
            }}

            /* ---------------- buttons ---------------- */
            .stButton > button {{
                border-radius: 10px;
                border: 1px solid {PRIMARY};
                font-weight: 600;
            }}
            .stButton > button:hover {{
                border-color: {PRIMARY_DARK};
                color: {PRIMARY_DARK};
            }}
            .stButton > button[kind="primary"] {{
                background-color: {PRIMARY};
                border-color: {PRIMARY};
            }}
            .stButton > button[kind="primary"]:hover {{
                background-color: {PRIMARY_DARK};
            }}

            /* ---------------- streamlit metrics (fallback use) ---------------- */
            div[data-testid="stMetric"] {{
                background: {BG_SOFT};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 14px 16px 10px 16px;
            }}
            div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-weight: 600; }}
            div[data-testid="stMetricValue"] {{ color: {PRIMARY} !important; }}

            div[data-testid="stDataFrame"] {{
                border: 1px solid {BORDER};
                border-radius: 10px;
                overflow: hidden;
            }}

            /* hide Streamlit's default auto-generated page list --
               we draw our own branded nav via render_sidebar() instead */
            [data-testid="stSidebarNav"] {{
                display: none;
            }}

            /* ---------------- sidebar ---------------- */
            section[data-testid="stSidebar"] {{
                background-color: #FFFFFF !important;
                border-right: 1px solid {BORDER};
            }}
            section[data-testid="stSidebar"] * {{
                color: {TEXT} !important;
            }}
            section[data-testid="stSidebar"] a {{
                color: {TEXT} !important;
                font-weight: 500;
                border-radius: 10px;
            }}
            section[data-testid="stSidebar"] a:hover {{
                background-color: {BG_SOFT} !important;
                color: {PRIMARY} !important;
            }}
            section[data-testid="stSidebar"] a[aria-current="page"] {{
                background-color: {PRIMARY} !important;
                color: #FFFFFF !important;
                font-weight: 700;
            }}
            section[data-testid="stSidebar"] a[aria-current="page"] span {{
                color: #FFFFFF !important;
            }}

            div[data-testid="stAlert"] {{ border-radius: 10px; }}
            button[data-baseweb="tab"] {{ font-weight: 600; }}
            hr {{ border-color: {BORDER}; }}

            /* ---------------- custom sidebar branding ---------------- */
            .vai-sidebar-logo {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 4px 4px 18px 4px;
                margin-bottom: 10px;
                border-bottom: 1px solid {BORDER};
            }}
            .vai-sidebar-logo .logo-icon {{
                width: 38px;
                height: 38px;
                border-radius: 10px;
                background: {PRIMARY};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
            }}
            .vai-sidebar-logo .logo-text b {{
                display: block;
                font-size: 15px;
                font-weight: 800;
            }}
            .vai-sidebar-logo .logo-text span {{
                display: block;
                font-size: 11px;
                color: {TEXT_MUTED} !important;
            }}

            .vai-sidebar-profile {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                border-radius: 10px;
                background: {BG_SOFT};
                margin-top: 14px;
            }}
            .vai-sidebar-profile .avatar {{
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: {PRIMARY};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 15px;
                font-weight: 700;
                flex-shrink: 0;
            }}
            .vai-sidebar-profile b {{
                display: block;
                font-size: 13px;
            }}
            .vai-sidebar-profile span {{
                display: block;
                font-size: 11px;
                color: {TEXT_MUTED} !important;
            }}

            .vai-logout-link a {{
                color: {RED} !important;
                font-weight: 600;
            }}
            .vai-logout-link a:hover {{
                background-color: {RED_BG} !important;
                color: {RED} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, subtitle: str = "", right_html: str = ""):
    """Icon-in-a-box + title + subtitle header, with optional right-aligned HTML (e.g. date/time)."""
    st.markdown(
        f"""
        <div class="vai-header">
            <div class="left">
                <div class="icon">{icon}</div>
                <div class="titles">
                    <h1>{title}</h1>
                    {f'<p>{subtitle}</p>' if subtitle else ''}
                </div>
            </div>
            <div>{right_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str):
    st.markdown(f'<div class="vai-section-label">{text}</div>', unsafe_allow_html=True)


def metric_card(icon: str, label: str, value: str, sub: str, color: str, bg: str):
    """Icon-circle stat card matching the reference dashboard (Total Students / Present Today / etc.)."""
    st.markdown(
        f"""
        <div class="vai-stat">
            <div class="stat-icon" style="background:{bg}; color:{color};">{icon}</div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-sub">{sub}</div>
            <div class="stat-bar" style="background:{color}; opacity:0.85;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def quick_action_card(icon: str, title: str, subtitle: str, color: str, bg: str):
    """Colored icon + title + subtitle row used inside a quick-action tile.
    Call this INSIDE a st.container()/column, followed by st.page_link for the actual click target."""
    st.markdown(
        f"""
        <div class="vai-action" style="background:{bg};">
            <div class="a-icon" style="background:#FFFFFF; color:{color};">{icon}</div>
            <div>
                <p class="a-title">{title}</p>
                <p class="a-sub">{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(admin_name: str = "Admin", admin_role: str = "Administrator"):
    """
    Custom branded sidebar (logo header + icon nav + logout + profile card),
    replacing Streamlit's plain default page list. Call this once near the
    top of EVERY page, right after apply_theme().

    Note: Logout here is a visual element only -- this project has no
    authentication system wired up yet, so it doesn't actually log anyone
    out. Wire it to real auth later if you add login functionality.
    """
    with st.sidebar:
        st.markdown(
            f"""
            <div class="vai-sidebar-logo">
                <div class="logo-icon">🎙</div>
                <div class="logo-text">
                    <b>VoiceAttendAI</b>
                    <span>Smart Attendance System</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("pages/dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/register.py", label="Student Registration", icon="📝")
        st.page_link("pages/student.py", label="Students", icon="👥")
        st.page_link("pages/voice_registration.py", label="Voice Registration", icon="🎙")
        st.page_link("pages/attendance.py", label="AI Voice Attendance", icon="🎤")

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="vai-logout-link">',
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="Logout", icon="🚪")
        st.markdown('</div>', unsafe_allow_html=True)

        initials = "".join([w[0] for w in admin_name.split()[:2]]).upper()
        st.markdown(
            f"""
            <div class="vai-sidebar-profile">
                <div class="avatar">{initials}</div>
                <div>
                    <b>Welcome, {admin_name}</b>
                    <span>{admin_role}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
