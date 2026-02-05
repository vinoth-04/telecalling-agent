from app.intents.intent_detector import detect_intent

def run_test(text):
    intent, confidence = detect_intent(text)
    print(f"INPUT     : {text}")
    print(f"INTENT    : {intent}")
    print(f"CONFIDENCE: {confidence}")
    print("-" * 40)

if __name__ == "__main__":
    run_test("I want to book a new appointment")
    run_test("Can you reschedule my appointment")
    run_test("What time do you open")
    run_test("My tooth is bleeding badly")
    run_test("I want to talk to a human agent")
    run_test("I have a question")
