import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_config():
    print("Running Configuration Check...")
    
    # Load .env
    _project_root = Path(__file__).resolve().parent.parent
    load_dotenv(_project_root / ".env", override=False)
    
    # Define required/optional variables to check
    secrets_to_check = [
        "OPENAI_API_KEY",
        "GROQ_API_KEY",
        "DEEPGRAM_API_KEY",
        "CARTESIA_API_KEY",
        "ELEVEN_LABS_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "JWT_SECRET"
    ]
    
    non_secrets_to_check = [
        "DATABASE_URL",
        "LLM_PROVIDER",
        "TTS_PROVIDER",
        "TRANSPORT_MODE"
    ]
    
    print("\n--- Core Configuration ---")
    for var in non_secrets_to_check:
        val = os.getenv(var)
        if val:
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} is missing or empty")

    print("\n--- Secrets Configuration ---")
    all_good = True
    for var in secrets_to_check:
        val = os.getenv(var)
        if val:
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} is missing or empty")
            all_good = False
            
    print("\nConfiguration check complete.")
    if not all_good:
        print("Note: Some secrets are missing. This might be fine if you are not using that specific provider.")
    
if __name__ == "__main__":
    check_config()
