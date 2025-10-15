import requests
import json
import time
import os
import google.generativeai as genai
import re

# --- Configuration for Gemini API ---
GEMINI_MODEL = "models/gemini-2.5-flash"

MAX_RETRIES = 5
INITIAL_DELAY = 1.0  # seconds

SYSTEM_INSTRUCTION = (
    "You are a professional executive assistant specializing in synthesizing meeting discussions into structured summaries. "
    "Your response must always follow the exact markdown format below — with the same section headers, symbols, and structure — so that it can be parsed reliably by regex. "
    "Do not include any commentary, explanations, or extra formatting outside this structure.\n\n"
    "The required output format is:\n\n"
    "**Summary:**  \n"
    "<Concise summary of the meeting, written in clear paragraph form. Focus on context, main discussion points, and outcomes.>\n\n"
    "**Key Decisions:**  \n"
    "* <List each major decision as a separate bullet point.>\n"
    "* <Ensure each decision is self-contained and specific.>\n\n"
    "**Action Items:**  \n"
    "**<Person/Role>**: <Clearly defined task or responsibility>  \n"
    "**<Person/Role>**: <Clearly defined task or responsibility>  \n\n"
    "Guidelines:  \n"
    "- Always include all three sections (“Summary,” “Key Decisions,” and “Action Items”) even if one is empty — in that case, write “None.”  \n"
    "- Do not rename, reorder, or reformat the section headers.  \n"
    "- Maintain exact Markdown syntax: double asterisks for headers and names, colons after headers and names, and proper line breaks.  \n"
    "- Each Action Item must begin with “**<Person/Role>**:” (bold name, colon, then task).  \n"
    "- Keep all text concise, factual, and in professional business English.  \n"
    "- If the transcript is unclear, infer meaning where reasonable and mark uncertain parts as “[unclear]”.  \n\n"
    "Your goal:  \n"
    "Summarize the meeting effectively, list all key decisions, and clearly specify action items with responsible individuals or roles in the required structured format."
)


def summarize_transcript(transcript: str) -> dict:
    import re
    genai.configure(api_key="AIzaSyACjkkfTXUVjur34CGmdDH_EHQkFY1CYzk")
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = f"{SYSTEM_INSTRUCTION}\n\nTRANSCRIPT:\n{transcript}"

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            print("Raw Gemini Output:\n", response.text)

            text = response.text.strip()

            # --- Extract sections using regex ---
            # Try to extract summary, decisions, and actions as separate sections
            summary_match = re.search(r"(?s)\*\*Summary:?\*\*(.*?)(\*\*Key Decisions:?\*\*|\*\*Action Items:?\*\*|$)", text)
            decisions_match = re.search(r"(?s)\*\*Key Decisions:?\*\*(.*?)(\*\*Action Items:?\*\*|$)", text)
            actions_match = re.search(r"(?s)\*\*Action Items:?\*\*(.*)", text)

            summary_text = summary_match.group(1).strip() if summary_match else text
            decisions_raw = decisions_match.group(1).strip() if decisions_match else ""
            actions_raw = actions_match.group(1).strip() if actions_match else ""

            # Remove any Key Decisions or Action Items sections from summary_text
            summary_text = re.split(r"\*\*Key Decisions:?\*\*|\*\*Action Items:?\*\*", summary_text)[0].strip()

            # Split bullet points for key decisions (accepts * or - as bullet)
            key_decisions = re.findall(r"(?:\*|-)+\s+(.+)", decisions_raw)
            action_items = []
            for item in re.findall(r"(?:\*\*|-\*\*)\s*(.+)", actions_raw):
                m = re.match(r"\*\*(.+?)\*\*:\s*(.+)", item)
                if m:
                    action_items.append({"assigned_to": m.group(1), "task": m.group(2), "due_date": "Not specified"})
                else:
                    action_items.append({"assigned_to": "Unknown", "task": item, "due_date": "Not specified"})

            # If the only key_decision is a 'no decisions' message, treat as empty
            if key_decisions and all('no key decision' in d.lower() or 'none' in d.lower() for d in key_decisions):
                key_decisions = []
            # If the only action_item is a 'no action items' message, treat as empty
            if action_items and all('no action item' in a['task'].lower() or 'none' in a['task'].lower() for a in action_items):
                action_items = []

            return {
                "summary": summary_text,
                "key_decisions": key_decisions,
                "action_items": action_items
            }

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (2 ** attempt)
                print(f"API Error (Attempt {attempt + 1}): {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Failed to call Gemini API after {MAX_RETRIES} attempts.") from e

    return {"summary": "No summary generated after retries.", "key_decisions": [], "action_items": []}

