import pyttsx3
import threading

class VoiceSynthesizer:
    """
    Level 7: Auditory Output (The 'Mouth' of the Organism).
    Uses pyttsx3 to speak high-priority alerts.
    """
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160) # Slightly faster
            self.engine.setProperty('volume', 0.9)
            
            # Select a voice (try to find a good one)
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id) # Default
                
            self.available = True
            print("[VOICE] Vocal Cords Initialized.")
        except Exception as e:
            print(f"[VOICE] Initialization Failed: {e}")
            self.available = False

    def speak(self, text: str):
        """Speaks text in a non-blocking thread."""
        if not self.available: return
        
        def _speak():
            try:
                # Re-initialize for thread safety if needed or just use engine
                # pyttsx3 runAndWait blocks, so we run in thread
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[VOICE] Error speaking: {e}")

        threading.Thread(target=_speak).start()

    def announce_event(self, event_type: str, payload: dict):
        """Standardized announcements."""
        if "METABOLIC_STRESS" in event_type:
            self.speak("Warning. Metabolic stress detected. Conservation mode active.")
        elif "VISUAL_ANALYSIS" in event_type:
            sentiment = payload.get("sentiment", "UNKNOWN")
            self.speak(f"Visual Cortex analyzed. Sentiment is {sentiment}.")
        elif "GOAL_ACHIEVED" in event_type:
            self.speak("Strategic Goal Achieved.")
