"""The titles, notes and group names of the shipped workflows."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.\n"

SHARED_TEXTS = {
    "start": "Start Here",
    "input": "Input",
    "ask": "Ask",
    "image": "Image",
    "video": "Video",
    "speech": "Speech",
    "transcript": "Transcript",
    "search": "Search",
    "decision": "Decision",
    "answer": "Answer",
}
WORKFLOW_TEXTS = {
    "chat-01-ask-a-question": {
        "start": (
            KEY_STEP + "2. Edit **prompt** on **Chat: Ask**. It sends one paid OpenRouter request.\n"
            "3. Press **Run**. The answer appears in **Preview as Text**."
        ),
    },
    "chat-02-describe-an-image": {
        "start": (
            KEY_STEP + "2. Upload an image in **Load Image**.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request with the image.\n"
            "4. Press **Run**."
        ),
    },
    "chat-03-caption-a-folder": {
        "start": (
            KEY_STEP + "2. Put the images in a folder inside ComfyUI's input folder and choose it in **Load Image "
            "(from Folder)**.\n"
            "3. **Chat: Ask** runs once per image, so each image is one paid OpenRouter request. The captions are "
            "saved beside copies of the images in `output/openrouter-captions`.\n"
            "4. Press **Run**."
        ),
    },
    "chat-04-compare-two-images": {
        "start": (
            KEY_STEP + "2. Upload the first image in **Before** and the second in **After**.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request with both images, each at its own size.\n"
            "4. Press **Run**."
        ),
    },
    "chat-05-summarize-a-document": {
        "start": (
            KEY_STEP + "2. Put a PDF or text file in ComfyUI's input folder, press R, and choose it in **Chat: "
            "Attach Document**.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request with the document.\n"
            "4. Press **Run**."
        ),
    },
    "chat-06-improve-a-prompt": {
        "start": (
            KEY_STEP + "2. Describe the picture in **prompt** on **Chat: Ask**. It sends one paid OpenRouter "
            "request that writes an image prompt.\n"
            "3. **Image: Generate** sends one paid OpenRouter request that draws it.\n"
            "4. Press **Run**."
        ),
    },
    "chat-07-read-fields-from-a-photo": {
        "start": (
            KEY_STEP + "2. Upload a photo of a product with its price in **Load Image**.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request. Its **answer schema** asks for a JSON answer "
            "with the fields `name` and `price`, which **Extract JSON String** reads.\n"
            "4. Press **Run**."
        ),
    },
    "chat-08-hold-a-conversation": {
        "start": (
            KEY_STEP + "2. The second **Chat: Ask** continues the first one's conversation. Each sends one paid "
            "OpenRouter request.\n"
            "3. Press **Run**."
        ),
    },
    "chat-09-answer-out-loud": {
        "start": (
            KEY_STEP + "2. The model answers in speech. Its **outputs** choice is **audio and text**; choose "
            "**text** for a written answer only.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request.\n"
            "4. Press **Run** and play the answer in **Preview Audio**."
        ),
    },
    "image-01-generate-an-image": {
        "start": (
            KEY_STEP + "2. Edit **prompt** on **Image: Generate**. It sends one paid OpenRouter request.\n"
            "3. Press **Run**. **Save Image** shows and saves the result."
        ),
    },
    "image-02-edit-an-image": {
        "start": (
            KEY_STEP + "2. Upload the photo in **Load Image** and describe the change in **prompt**.\n"
            "3. **Image: Generate** sends one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "image-03-combine-two-images": {
        "start": (
            KEY_STEP + "2. Upload the product in **Product** and the room in **Scene**.\n"
            "3. **Image: Generate** sends one paid OpenRouter request with both images.\n"
            "4. Press **Run**."
        ),
    },
    "image-04-draw-a-vector-logo": {
        "start": (
            KEY_STEP + "2. Describe the logo in **prompt**. The vector model returns SVG, which **Save SVG** "
            "saves.\n"
            "3. **Image: Generate** sends one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "image-05-draw-with-a-chat-model": {
        "start": (
            KEY_STEP + "2. A chat model that draws returns the image and a description together.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "video-01-make-a-video": {
        "start": (
            KEY_STEP + "2. Describe the video in **prompt** and choose its **duration (seconds)**. Video is "
            "priced per second.\n"
            "3. **Video: Generate** sends one paid OpenRouter request and waits for the video.\n"
            "4. Press **Run**."
        ),
    },
    "video-02-animate-an-image": {
        "start": (
            KEY_STEP + "2. Upload the first frame in **Load Image** and describe the motion in **prompt**.\n"
            "3. **Video: Generate** sends one paid OpenRouter request and waits for the video.\n"
            "4. Press **Run**."
        ),
    },
    "video-03-draw-then-animate": {
        "start": (
            KEY_STEP + "2. **Image: Generate** sends one paid OpenRouter request that draws the first frame.\n"
            "3. **Video: Generate** sends one paid OpenRouter request that animates it.\n"
            "4. Press **Run**."
        ),
    },
    "video-04-download-a-video": {
        "start": (
            KEY_STEP + "2. Run **Video: Generate** first and cancel it, or close ComfyUI while it waits; then "
            "choose the job in **unfinished job** and press R to refresh the list if it is missing.\n"
            "3. **Video: Download** only checks and downloads the job, which costs nothing more.\n"
            "4. Press **Run**."
        ),
    },
    "audio-01-read-text-aloud": {
        "start": (
            KEY_STEP + "2. Write the text in **text to speak** on **Audio: Speak**. It sends one paid "
            "OpenRouter request.\n"
            "3. Press **Run**. **Save Audio** plays and saves the speech."
        ),
    },
    "audio-02-transcribe-a-recording": {
        "start": (
            KEY_STEP + "2. Upload a recording of at most about a minute in **Load Audio**.\n"
            "3. **Audio: Transcribe** sends one paid OpenRouter request. **Save Text** saves the transcript, and "
            "**Preview as Text** shows the subtitles.\n"
            "4. Press **Run**."
        ),
    },
    "audio-03-clone-a-voice": {
        "start": (
            KEY_STEP + "2. Upload a clean 10 to 30 second recording of one voice, and write what it says in "
            "**what the sample says**.\n"
            "3. **Audio: Speak** sends one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "audio-04-translate-a-recording": {
        "start": (
            KEY_STEP + "2. Upload a recording in **Load Audio**.\n"
            "3. **Audio: Transcribe**, **Chat: Ask**, and **Audio: Speak** each send one paid OpenRouter "
            "request: transcript, translation, then speech.\n"
            "4. Press **Run**."
        ),
    },
    "search-01-compare-texts": {
        "start": (
            KEY_STEP + "2. Write one item per line in **texts**; the first line is compared with every other.\n"
            "3. **Search: Embed** sends one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "search-02-rank-documents": {
        "start": (
            KEY_STEP + "2. Write the **query**, and one document per line in **documents**.\n"
            "3. **Search: Rank** sends one paid OpenRouter request.\n"
            "4. Press **Run**. The documents come back best first."
        ),
    },
    "search-03-pick-the-best-image": {
        "start": (
            KEY_STEP + "2. **Image: Generate** sends one paid OpenRouter request that draws four images.\n"
            "3. **Search: Rank** gathers all four into one paid OpenRouter request and keeps the best.\n"
            "4. Press **Run**."
        ),
    },
    "decision-01-sort-a-ticket": {
        "start": (
            KEY_STEP + "2. Edit the ticket in **situation** and the three questions: which team, whether it is a "
            "bug, and how urgent it is.\n"
            "3. **Decision: Ask** sends one paid OpenRouter request and answers with probabilities.\n"
            "4. Press **Run**."
        ),
    },
    "decision-02-sort-a-voicemail": {
        "start": (
            KEY_STEP + "2. Upload a voicemail in **Load Audio**.\n"
            "3. **Audio: Transcribe** and **Decision: Ask** each send one paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "decision-03-check-an-image-before-saving": {
        "start": (
            KEY_STEP + "2. Write the brief. **Image: Generate**, **Chat: Ask**, and **Decision: Ask** each send "
            "one paid OpenRouter request: the image, its description, and the check.\n"
            "3. **If/Else Switch** is a ComfyUI node marked as a beta. Only the branch it picks runs; here it "
            "picks the folder the image is saved in.\n"
            "4. Press **Run**."
        ),
    },
    "decision-04-route-a-request": {
        "start": (
            KEY_STEP + "2. Write the request. **Decision: Ask** sends one paid OpenRouter request that decides "
            "whether it wants a photo or an illustration.\n"
            "3. **If/Else Switch** is a ComfyUI node marked as a beta. Only the branch it picks runs, so only one "
            "**Image: Generate** sends a paid OpenRouter request.\n"
            "4. Press **Run**."
        ),
    },
    "decision-05-verify-then-escalate": {
        "start": (
            KEY_STEP + "2. Write the notes and the question. The first **Chat: Ask** answers with a cheap model, "
            "and **Decision: Ask** checks the answer against the notes; each sends one paid OpenRouter request.\n"
            "3. **If/Else Switch** is a ComfyUI node marked as a beta. Only the branch it picks runs, so the "
            "strong model's **Chat: Ask** sends a paid request only when the check fails.\n"
            "4. Press **Run**."
        ),
    },
    "options-01-choose-providers": {
        "start": (
            KEY_STEP + "2. **Request Options** asks OpenRouter for the cheapest provider and allows others as a "
            "fallback.\n"
            "3. **Chat: Ask** sends one paid OpenRouter request with those options.\n"
            "4. Press **Run**."
        ),
    },
}

__all__ = ["SHARED_TEXTS", "WORKFLOW_TEXTS"]
