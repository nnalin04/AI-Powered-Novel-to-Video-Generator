from dotenv import load_dotenv
import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

try:
    from ai_film_studio.config.settings import settings
except ImportError:
    print("❌ Could not import settings. Make sure you are in the project root.")
    sys.exit(1)

def check_creds():
    print("--- Checking Credentials & Configuration ---")
    
    # 1. Check Env File Loading
    if not os.path.exists(".env"):
        print("❌ .env file not found.")
        return
    
    print("✅ .env file found.")

    # 2. Check Critical Keys
    keys_to_check = [
        "GOOGLE_API_KEY",
        "REPLICATE_API_TOKEN",
        "ELEVENLABS_API_KEY"
    ]
    
    all_good = True
    for key in keys_to_check:
        val = getattr(settings, key, None)
        # Check if set and not default placeholder (simple check)
        if val and "..." not in str(val) and str(val) != "None":
            print(f"✅ {key}: Configured")
        else:
            print(f"❌ {key}: Missing or Placeholder detected")
            all_good = False

    # 3. Check Service Account File
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    
    # Resolve Docker path to Host path for local verification
    host_creds_path = creds_path
    if creds_path and creds_path.startswith("/app/"):
        host_creds_path = creds_path.replace("/app/", os.getcwd() + "/")
        print(f"ℹ️  Resolving Docker path {creds_path} to Host path for local check.")

    if host_creds_path and os.path.exists(host_creds_path):
         print(f"✅ Service Account File found at: {host_creds_path}")
         try:
             with open(host_creds_path, "r") as f:
                 creds = json.load(f)
                 project_id = creds.get("project_id")
                 if project_id:
                     print(f"✅ Service Account Project ID: {project_id}")
                 else:
                     print("❌ Service Account Project ID NOT found in file.")
                     all_good = False
         except Exception as e:
             print(f"❌ Could not read Service Account file: {e}")
             all_good = False
    elif creds_path:
         print(f"❌ Service Account File NOT found at: {host_creds_path}")
         all_good = False

    # 4. Summary
    if all_good:
        print("\n🎉 Configuration looks valid! You are likely ready to run.")
    else:
        print("\n⚠️  Some configurations are missing or incorrect. Please check .env.")

if __name__ == "__main__":
    check_creds()
