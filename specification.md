# Product Specification Document: Workout Plan Generator

## 1. Overview & Objective
The goal of this project is to build a single-page Streamlit web application that collects structured user fitness profile details and uses an LLM via the **Groq API** to generate a highly tailored, usable, weekly workout plan.

Rather than accepting a single generic text input, the application enforces structured inputs to provide full context to the LLM (mimicking a human personal trainer) while preventing generic outputs.

---

## 2. Tech Stack Requirements
* **Language & Runtime:** Python 3.10+
* **UI Framework:** Streamlit
* **LLM Provider:** Groq API (via `groq` official SDK)
* **Configuration / Secrets Management:** Environment variables via `.env` or Streamlit Secrets (`st.secrets`)
* **Code Standards:** Explicit typing (`typing` module / standard type annotations), modular design, robust error handling with `try/except` blocks.

---

## 3. UI & Feature Architecture

### 3.1 Input Component Requirements (Sidebar or Form View)
The app must collect the following structured user inputs:

1. **Fitness Goal** (`Dropdown / Selectbox`):
   * `Build muscle`
   * `Lose fat`
   * `General fitness`
   * `Improve endurance`
2. **Experience Level** (`Dropdown / Selectbox`):
   * `Beginner`
   * `Intermediate`
   * `Advanced`
3. **Days Available Per Week** (`Slider / Number Input`):
   * Range: `1` to `7` days (Default: `3`)
4. **Equipment Access** (`Dropdown / Multiselect`):
   * Options: `No equipment (Bodyweight)`, `Home dumbbells`, `Full gym`
5. **Injuries or Limitations** (`Text Input / Text Area`, *Optional*):
   * Examples: *"bad knees"*, *"no overhead pressing"*, *"lower back issues"*

### 3.2 Action Controls
* **Primary Action:** `Generate Plan` button
* **Secondary Action (Stretch Goals):**
  * `Regenerate` button (Generates a new variant without re-entering details)
  * `Download Plan` button (Export generated plan as `.txt` or `.md`)

---

## 4. Prompt Engineering & System Design

### 4.1 Key Prompting Guidelines
* **Strict Constraint Adherence:** Explicitly enforce equipment availability and injury/limitation restrictions.
* **Structured Markdown Output:** Force the model to organize the plan day-by-day (e.g., Day 1, Day 2) with explicit Exercises, Sets, Reps, and Rest intervals.
* **Scope & Safety Guidelines:** 
  * Avoid making medical claims or giving physical therapy advice.
  * If any injuries/limitations are specified, automatically append a standard liability disclaimer:  
    > *"Disclaimer: This plan is for informational purposes only. Please consult a healthcare professional before exercising with pre-existing injuries or conditions."*

### 4.2 LLM Invocation Logic (Python Function Specs)

```python
from typing import Dict, Any, Optional

def generate_workout_plan(
    goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    limitations: Optional[str] = None
) -> str:
    """
    Constructs a structured prompt based on user context and queries the Groq API.

    Parameters:
        goal (str): User's primary goal (e.g., 'Build muscle').
        experience_level (str): 'Beginner', 'Intermediate', or 'Advanced'.
        days_per_week (int): Number of workout days (1-7).
        equipment (str): Available fitness equipment.
        limitations (Optional[str]): Pre-existing injuries or physical limitations.

    Returns:
        str: Generated workout plan formatted in Markdown or an error message string.
    """
```

---

## 5. Error Handling & Edge Cases

| Scenario / Edge Case | Expected Behavior / System Handling |
| :--- | :--- |
| **Invalid Inputs (e.g., 0 days selected)** | Streamlit validation warning (`st.warning`) prevents API submission and displays a helpful user message. |
| **Missing Groq API Key** | Displays clear setup instructions to add `GROQ_API_KEY` to `.env` or `.streamlit/secrets.toml`. |
| **API Failure (Rate limit, network error)** | Catch exception with `try/except` block and render `st.error("Unable to connect to Groq API. Please try again later.")`. |
| **Empty or Malformed LLM Response** | Return a graceful fallback message (`st.error("Received an invalid response from the generator. Please try again.")`). |

---

## 6. Functional & Technical Deliverables

1. **State Persistence (`st.session_state`):**
   * Generated workout plan must persist across page reruns or widget interactions.
2. **Code Structure:**
   * Clean separation of UI logic (Streamlit layout) and core business logic (Groq API wrapper function).
3. **Repository Deliverables:**
   * `app.py` - Main Streamlit application file.
   * `requirements.txt` - Dependencies (`streamlit`, `groq`, `python-dotenv`).
   * `.env.example` - Template for environment variables.
   * `README.md` - Setup and execution instructions.

---

## 7. Rubric & Evaluation Metrics

* **Input Validation & Crash Prevention (20%):** Enforces safe execution without crashing on missing or boundary values.
* **Structured Inputs & Prompt Integration (25%):** Correctly captures and maps all UI parameters into the prompt payload.
* **Prompt Design & Output Quality (30%):** Prompt produces clean, usable, formatted Markdown outputs respecting all constraints and safety disclaimers.
* **Error & Exception Handling (15%):** Graceful recovery from API key issues, network failures, or null responses.
* **Code Quality & Type Safety (10%):** Uses standard Python type annotations, modular functions, and clean design patterns.
```
