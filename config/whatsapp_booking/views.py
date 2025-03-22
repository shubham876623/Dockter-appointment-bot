import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from django.views.decorators.http import require_POST
from .services.cal_service import get_event_types, get_slots, book_slot
from .services.twilio_service import TwilioService
from .services.openai_service import GPTService

load_dotenv()

# Redis Client for session management
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """
    Handles incoming WhatsApp messages dynamically based on detected intent.
    """
    user_message = request.POST.get("Body", "").strip()
    sender_number = request.POST.get("From").split(":")[-1]
    session_key = f"user:{sender_number}"
    user_language = GPTService.detect_language(user_message)

    # Detect the user intent dynamically
    detected_intent = GPTService.determine_action(user_message)
    print(f"Detected Intent: {detected_intent}")

    # Default response for unexpected inputs
    response_text = GPTService.translate_text(
        "I'm sorry, I didn't understand that. How may I assist you?",
        user_language
    )

    # **Intent: Greeting (Resets Conversation)**
    if detected_intent == "GREETING":
        redis_client.delete(session_key)  # Clears session on greeting
        response_text = GPTService.translate_text(
            "Thank you for reaching out to Hello Hospitals. This is John. How can I assist you today?",
            user_language
        )

    # **Intent: Asking for Available Doctors**
    elif detected_intent == "DEPARTMENT_REQUEST":
        doctors_list = get_event_types()
        department_response = GPTService.department_doctor_name(user_message, doctors_list)

        if "Sorry" in department_response:
            response_text = GPTService.translate_text(department_response, user_language)
        else:
            response_text = GPTService.translate_text(f"{department_response}", user_language)
            redis_client.hset(session_key, "last_department_request", user_message)

    # **Intent: Describing Symptoms (Recommend Best Doctor)**
    elif detected_intent == "CONDITION_DESCRIPTION":
        doctors_list = get_event_types()
        best_doctor = GPTService.recommend_best_doctor(user_message, doctors_list)

        if best_doctor == "UNKNOWN":
            response_text = GPTService.translate_text(
                "I'm sorry, I couldn't find a suitable doctor based on your condition. Would you like recommendations for another department?",
                user_language
            )
        else:
            best_doctor = "vinay"
            redis_client.hset(session_key, "doctor", best_doctor)
            response_text = GPTService.translate_text(
                f"I understand. Based on your condition, Dr. {best_doctor} might be the best option. "
                "Would you like me to book an appointment?",
                user_language
            )

    # **Intent: Appointment Booking Confirmation**
    elif detected_intent == "APPOINTMENT_BOOKING":
        if not redis_client.hexists(session_key, "booking_step"):
            response_text = GPTService.translate_text(
                "Great! May I know when you’d like to schedule the appointment?",
                user_language
            )
            redis_client.hset(session_key, "booking_step", "DATE_ASKED")

    # **Intent: Handling Date & Slot Selection**
    elif detected_intent == "SLOT_SELECTION":
        if redis_client.hget(session_key, "booking_step") == "DATE_ASKED":
            user_requested_time = user_message.strip()
            formatted_time = GPTService.format_requested_time(user_requested_time)

            if not formatted_time:
                response_text = GPTService.translate_text(
                    "I'm sorry, I couldn't understand the time you provided. Can you please rephrase it?",
                    user_language
                )
            else:
                # doctor_name = redis_client.hget(session_key, "doctor")
                doctor_name = "Neurology Test Meeting"
                if doctor_name:
                    doctor_event_id = next(
                        (d["id"] for d in get_event_types()["event_types"] if d["title"] == doctor_name),
                        None
                    )

                    if doctor_event_id:
                        available_slots = get_slots(doctor_event_id)
                        slot_available = GPTService.check_time_availability(formatted_time, available_slots)

                        if slot_available:
                            success = book_slot(doctor_event_id, formatted_time)

                            if success:
                                response_text = GPTService.translate_text(
                                    f"✅ Got it! Your appointment for {user_requested_time} with Dr. {doctor_name} is confirmed. "
                                    "You will receive a confirmation message shortly. Let us know if you need any help.",
                                    user_language
                                )
                                TwilioService.send_sms(sender_number, "✅ Your appointment is confirmed at {user_requested_time} with Dr. {doctor_name}")
                                redis_client.delete(session_key)  # Clear session after booking
                            else:
                                response_text = GPTService.translate_text(
                                    "There was an issue booking your appointment. Please try again.",
                                    user_language
                                )
                        else:
                            response_text = GPTService.translate_text(
                                f"Unfortunately, there are no available slots for your requested time ({user_requested_time}). "
                                "Would you like to choose another time?",
                                user_language
                            )
                    else:
                        response_text = GPTService.translate_text(
                            "I'm sorry, but I couldn't find the selected doctor. Can you please specify their name again?",
                            user_language
                        )
                else:
                    response_text = GPTService.translate_text(
                        "I couldn't find an active doctor selection. Please specify the doctor you'd like to book an appointment with.",
                        user_language
                    )

    # **Send response via Twilio WhatsApp**
    TwilioService.send_whatsapp(sender_number, response_text)

    return JsonResponse({"message": "Response sent"})
