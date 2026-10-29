
# -*- coding: utf-8 -*-
"""
Workout Plan Generator - Main Streamlit Application
Uses the Groq API to generate personalized weekly workout plans.
"""

import os
import streamlit as st
from typing import Optional
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, RateLimitError, APIStatusError

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def generate_workout_plan(
    goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    limitations: Optional[str] = None,
) -> str:
    """
    Constructs a structured prompt and queries the Groq API.

    Parameters:
        goal (str): The user primary fitness goal.
        experience_level (str): Beginner, Intermediate, or Advanced.
        days_per_week (int): Number of workout days (1-7).
        equipment (str): Available fitness equipment.
        limitations (Optional[str]): Pre-existing injuries or physical limitations.

    Returns:
        str: Generated workout plan in Markdown, or an error sentinel string.
    """
    if not GROQ_API_KEY:
        return "__ERROR_NO_KEY__"

    limitation_section: str = (
        f"\n- **Injuries / Limitations:** {limitations.strip()}"
        if limitations and limitations.strip()
        else "\n- **Injuries / Limitations:** None"
    )

    disclaimer: str = (
        "\n\n---\n> **Disclaimer:** This plan is for informational purposes only. "
        "Please consult a healthcare professional before exercising with pre-existing injuries or conditions."
        if limitations and limitations.strip()
        else ""
    )

    system_prompt: str = (
        "You are an expert personal trainer with 20 years of experience. "
        "Your job is to create highly personalized, safe, and effective weekly workout plans "
        "based on the user profile. Always respond in clean, well-structured Markdown. "
        "Organize the plan day-by-day with each day having a clear heading. "
        "For every exercise specify: Exercise name, Sets, Reps (or Duration), Rest interval, and a brief form tip. "
        "Strictly respect equipment limitations and any physical restrictions. "
        "Do NOT provide medical advice or physical therapy recommendations."
    )

    user_prompt: str = (
        f"Please create a complete {days_per_week}-day per week workout plan for the following profile:\n\n"
        f"- **Primary Goal:** {goal}\n"
        f"- **Experience Level:** {experience_level}\n"
        f"- **Days Per Week:** {days_per_week}\n"
        f"- **Equipment Available:** {equipment}"
        f"{limitation_section}\n\n"
        "Format the plan with:\n"
        "1. A brief introduction paragraph summarizing the plan approach.\n"
        "2. A weekly schedule overview table.\n"
        "3. Detailed day-by-day workout breakdowns with exercises, sets, reps, and rest times.\n"
        "4. General tips and recovery advice at the end.\n"
        f"{disclaimer}"
    )

    try:
        client: Groq = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.75,
            max_tokens=4096,
        )
        content: Optional[str] = response.choices[0].message.content
        if not content or not content.strip():
            return "__ERROR_EMPTY__"
        return content.strip()

    except RateLimitError:
        return "__ERROR_RATE_LIMIT__"
    except APIConnectionError:
        return "__ERROR_CONNECTION__"
    except APIStatusError as exc:
        return f"__ERROR_API__{exc.status_code}"
    except Exception:
        return "__ERROR_GENERIC__"


def resolve_error(raw: str) -> Optional[str]:
    """Maps internal error sentinels to user-friendly messages."""
    if raw == "__ERROR_NO_KEY__":
        return (
            "**Groq API Key not found.**\n\n"
            "Add your key to the .env file:\n`\nGROQ_API_KEY=your_key_here\n`\n"
            "Or add it to .streamlit/secrets.toml:\n`	oml\nGROQ_API_KEY = \"your_key_here\"\n`"
        )
    if raw == "__ERROR_EMPTY__":
        return "Received an invalid response from the generator. Please try again."
    if raw == "__ERROR_RATE_LIMIT__":
        return "Unable to connect to Groq API - rate limit exceeded. Please wait and try again."
    if raw == "__ERROR_CONNECTION__":
        return "Unable to connect to Groq API. Please check your internet connection and try again."
    if raw == "__ERROR_GENERIC__":
        return "Unable to connect to Groq API. Please try again later."
    if raw.startswith("__ERROR_API__"):
        code = raw.replace("__ERROR_API__", "")
        return f"Unable to connect to Groq API (HTTP {code}). Please try again later."
    return None


def main() -> None:
    st.set_page_config(
        page_title="Workout Plan Generator",
        page_icon="\U0001f4aa",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        [data-testid="stSidebar"] {
            background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
        }
        [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
        [data-testid="stSidebar"] label {
            color: #94a3b8 !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── Selectbox: dark background + bright text ───────────────────── */
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
            background-color: #1e293b !important;
            border-color: #334155 !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] * {
            background-color: transparent !important;
            color: #e2e8f0 !important;
            -webkit-text-fill-color: #e2e8f0 !important;
        }
        /* Dropdown menu list (open state) */
        [data-testid="stSidebar"] [data-baseweb="popover"] *,
        [data-testid="stSidebar"] [data-baseweb="menu"] * {
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
            -webkit-text-fill-color: #e2e8f0 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="menu"] [aria-selected="true"],
        [data-testid="stSidebar"] [data-baseweb="menu"] li:hover {
            background-color: #334155 !important;
        }
        .hero-header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 20px 60px rgba(99,102,241,0.35);
        }
        .hero-header h1 { color: white !important; font-size: 2.4rem !important; font-weight: 700 !important; margin: 0 !important; }
        .hero-header p { color: rgba(255,255,255,0.82) !important; font-size: 1.05rem !important; margin-top: 0.5rem !important; }
        .badge-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1.2rem; }
        .badge {
            background: #1e293b; border: 1px solid #334155; border-radius: 20px;
            padding: 0.3rem 0.9rem; font-size: 0.8rem; color: #94a3b8; font-weight: 500;
        }
        .badge span { color: #e2e8f0; font-weight: 600; }
        .stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }
        .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(99,102,241,0.4) !important; }

        /* Textarea text & placeholder to match dropdown text color */
        [data-testid="stSidebar"] textarea {
            color: #e2e8f0 !important;
            background-color: #1e293b !important;
        }
        [data-testid="stSidebar"] textarea::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "workout_plan" not in st.session_state:
        st.session_state["workout_plan"] = ""
    if "last_inputs" not in st.session_state:
        st.session_state["last_inputs"] = {}

    with st.sidebar:
        st.markdown("## \u2699\ufe0f Your Fitness Profile")
        st.markdown("---")

        goal: str = st.selectbox(
            "\U0001f3af Fitness Goal",
            options=["Build muscle", "Lose fat", "General fitness", "Improve endurance"],
        )
        experience_level: str = st.selectbox(
            "\U0001f4ca Experience Level",
            options=["Beginner", "Intermediate", "Advanced"],
        )
        days_per_week: int = st.slider(
            "\U0001f4c5 Days Available Per Week",
            min_value=1, max_value=7, value=3, step=1,
        )
        equipment: str = st.selectbox(
            "\U0001f3cb\ufe0f Equipment Access",
            options=["No equipment (Bodyweight)", "Home dumbbells", "Full gym"],
            index=2,
        )
        limitations: str = st.text_area(
            "\u26a0\ufe0f Injuries / Limitations (Optional)",
            placeholder='e.g. "bad knees", "no overhead pressing", "lower back issues"',
            height=100,
        )

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            generate_clicked: bool = st.button("\U0001f680 Generate", type="primary", use_container_width=True)
        with col_b:
            regenerate_clicked: bool = st.button(
                "\U0001f504 Regenerate",
                use_container_width=True,
                disabled=not bool(st.session_state["last_inputs"]),
            )

    st.markdown(
        """
        <div class="hero-header">
            <h1>\U0001f4aa Workout Plan Generator</h1>
            <p>AI-powered personalized weekly workout plans &mdash; built just for you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    should_generate: bool = generate_clicked or (
        regenerate_clicked and bool(st.session_state["last_inputs"])
    )

    if should_generate:
        if days_per_week < 1:
            st.warning("\u26a0\ufe0f Please select at least **1 day per week** to generate a plan.")
        else:
            st.session_state["last_inputs"] = {
                "goal": goal,
                "experience_level": experience_level,
                "days_per_week": days_per_week,
                "equipment": equipment,
                "limitations": limitations,
            }
            with st.spinner("\U0001f916 Crafting your personalized workout plan..."):
                result: str = generate_workout_plan(
                    goal=goal,
                    experience_level=experience_level,
                    days_per_week=days_per_week,
                    equipment=equipment,
                    limitations=limitations.strip() or None,
                )
            error_msg: Optional[str] = resolve_error(result)
            if error_msg:
                st.error(error_msg)
                st.session_state["workout_plan"] = ""
            else:
                st.session_state["workout_plan"] = result

    if st.session_state["workout_plan"]:
        inputs: dict = st.session_state["last_inputs"]
        lim_text: str = inputs.get("limitations", "").strip() or "None"
        st.markdown(
            f"""
            <div class="badge-row">
                <div class="badge">\U0001f3af Goal: <span>{inputs.get("goal","")}</span></div>
                <div class="badge">\U0001f4ca Level: <span>{inputs.get("experience_level","")}</span></div>
                <div class="badge">\U0001f4c5 Days/Week: <span>{inputs.get("days_per_week","")}</span></div>
                <div class="badge">\U0001f3cb\ufe0f Equipment: <span>{inputs.get("equipment","")}</span></div>
                <div class="badge">\u26a0\ufe0f Limitations: <span>{lim_text}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["workout_plan"])
        st.markdown("---")
        file_name: str = f"workout_plan_{inputs.get('goal','plan').lower().replace(' ','_')}.md"
        st.download_button(
            label="\U0001f4e5 Download Plan (.md)",
            data=st.session_state["workout_plan"],
            file_name=file_name,
            mime="text/markdown",
        )
    else:
        st.info("\U0001f448 **Set your fitness profile** in the sidebar and click **Generate** to get started!")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### \U0001f3af Goal-Oriented\nPlans tailored to your exact goal - muscle, fat loss, or endurance.")
        with c2:
            st.markdown("### \U0001f3cb\ufe0f Equipment-Aware\nWorks with bodyweight only, home dumbbells, or a full gym.")
        with c3:
            st.markdown("### \U0001f6e1\ufe0f Injury-Conscious\nSpecify any limitations and the plan automatically avoids aggravating movements.")


if __name__ == "__main__":
    main()
