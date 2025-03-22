import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class GPTService:
    @staticmethod
    def query(prompt, max_tokens=100):
        """
        Sends a query to OpenAI and returns the response.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    @classmethod
    def detect_language(cls, message):
        """
        Detects the language of the given message.
        """
        prompt = f'Identify the language of this text: "{message}" Respond only with the language name.'
        return cls.query(prompt, max_tokens=10)

    @classmethod
    def translate_text(cls, text, language):
        """
        Translates text to the user's preferred language.
        """
        if language.lower() == 'english':
            return text
        prompt = f'Translate this text to {language}: "{text}"'
        return cls.query(prompt)

    @classmethod
    def determine_action(cls, user_message, chat_history=""):
        """
        Determines the intent of the user's message.
        """
        prompt = f"""
        The user said: "{user_message}"
        Chat history:
        "{chat_history}"

        Identify the intent:
        - "GREETING" if greeting.
        - "LANGUAGE_CHANGE" if they request a language switch.
        - "DEPARTMENT_REQUEST" if asking about doctors.
        - "CONDITION_DESCRIPTION" if describing symptoms.
        - "DOCTOR_CONFIRMATION" if confirming a doctor.
        - "APPOINTMENT_BOOKING" if asking to book an appointment.
        - "SLOT_SELECTION" if providing a specific time for booking.
        - "OTHER" if unclear.

        Respond only with the intent name.
        """
        return cls.query(prompt, max_tokens=20).strip().upper()

    @classmethod
    def department_doctor_name(cls, user_message, doctors):
        """
        Finds available doctors based on the user's requested department.
        """
        doctors_data = json.dumps(doctors["event_types"], indent=2)

        prompt = f"""
        The user is asking about available doctors: "{user_message}"
        
        The hospital has the following doctors:
        {doctors_data}

        - Identify the department the user is asking for.
        - Extract and return ONLY the names of doctors in that department.
        - Format: "Certainly! We have Dr. [Doctor1], Dr. [Doctor2] available in our [Department] Department. Do you have a preference?"
        - If no doctors are found, respond: "I'm sorry, but we do not have any doctors available in the [Department] department."
        """
        return cls.query(prompt)

    @classmethod
    def recommend_best_doctor(cls, user_message, doctors_list):
        """
        Identifies the most experienced doctor based on symptoms.
        """
        doctors_data = json.dumps(doctors_list["event_types"], indent=2)
       
        prompt = f"""
        The user described their condition: "{user_message}"

        The available doctors are:
        {doctors_data}

        - Find the most experienced doctor related to the symptoms.
        - If experience is missing, pick the first available doctor in the correct department.
        - Return ONLY the doctor's name.
        - If no suitable doctor is found, return "UNKNOWN".
        """
        return cls.query(prompt).strip()

    @classmethod
    def check_time_availability(cls, requested_time, available_slots):
        """
        Checks if the requested appointment time is available.
        """
        available_times = available_slots.get("slots", [])

        prompt = f"""
        The user requested an appointment at: "{requested_time}"

        The available slots are:
        {json.dumps(available_times, indent=2)}

        - Check if the requested time exactly matches an available slot.
        - If available, return "AVAILABLE".
        - If not, suggest the **closest available slot**.
        """
        return cls.query(prompt, max_tokens=20).strip().upper()

    @classmethod
    def format_requested_time(cls, user_time):
        """
        Converts user-provided time into ISO format.
        """
        prompt = f"""
        Convert this time into ISO format **YYYY-MM-DDTHH:MM:SS+05:30**.

        - User input: "{user_time}"
        - Convert relative times (e.g., "tomorrow at 5 PM") to exact date and time.
        - If the input is already in ISO format, return as is.
        - If the input is unclear, return "INVALID".
        """
        formatted_time = cls.query(prompt, max_tokens=50).strip()
        return formatted_time if formatted_time != "INVALID" else None
