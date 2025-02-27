import os
import google.generativeai as genai
# The cache file helps reduce the possibility of verses being repeated too often. It can be cleared.
CACHE_FILE = "verse_cache.txt"

def load_cached_verses():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_verse_to_cache(verse):
    with open(CACHE_FILE, "a") as f:
        f.write(verse + "\n")

def update_motd(verse):
    """Writes the provided verse to /etc/motd."""
    motd_file = "/etc/motd"
    try:
        with open(motd_file, "w") as f:
            f.write(verse + "\n")
        print("Successfully updated /etc/motd with the following verse:")
        print(verse)
    except PermissionError:
        print("Error: Permission denied. Please run the script with root privileges (e.g., using sudo).")
    except Exception as e:
        print(f"An error occurred while updating /etc/motd: {e}")

# Configure your API key
GOOGLE_API_KEY = "YOUR_API_KEY_GOES_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# Generation configuration
generation_config = {
    "temperature": 0.8,    # Experiment with 0.8-0.9 for variety.
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 10000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

# Refined prompt instructing the model to output only the Bible verse and its reference.
prompt = (
    "Please provide a completely random Bible verse for the day. "
    "Output only the full text of the verse along with its reference (book, chapter, and verse) with no additional commentary, introductions, or extra text. "
    "Also, avoid commonly cited verses like John 3:16 or Psalm 118:24."
)

cached_verses = load_cached_verses()

# Try generating until we get a verse that's not in the cache
max_attempts = 5
for attempt in range(max_attempts):
    response = chat_session.send_message(prompt)
    verse = response.text.strip()
    if verse not in cached_verses:
        print("Generated verse:")
        print(verse)
        save_verse_to_cache(verse)
        update_motd(verse)
        break
    else:
        print(f"Attempt {attempt+1}: Repeated verse found. Retrying...")
else:
    print("Could not generate a unique verse after several attempts. Please try again later.")