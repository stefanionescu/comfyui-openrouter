"""The titles, notes and group names of the shipped workflows."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.\n"
PRICES = "Prices are in **OpenRouter models**; each request's charge is at openrouter.ai/activity."

SHARED_TEXTS = {
    "start": "Start Here",
    "using": "Using This Workflow",
    "input": "Input",
    "write": "Write",
    "check": "Check",
    "save": "Save",
    "candidates": "Candidates",
    "choose": "Choose",
    "draft": "Draft",
    "edit": "Edit",
    "logo": "Logo",
    "frame": "First Frame",
    "video": "Video",
    "transcript": "Transcript",
    "reply": "Reply",
    "dub": "Dub",
    "search": "Search",
    "answer": "Answer",
    "escalate": "Escalate",
}
WORKFLOW_TEXTS = {
    "chat-01-write-a-product-listing": {
        "start": (
            KEY_STEP + "2. Upload two photos in **Product Photo (Front)** and **Product Photo (Detail)**.\n"
            "3. Choose the spec sheet, a PDF or text file in ComfyUI's input folder, in **Spec Sheet**.\n"
            "4. Press **Run**. The listing is saved as JSON under `listings/approved` or `listings/review`."
        ),
        "using": (
            "**Write the Listing** reads both photos and the spec sheet and answers in a fixed JSON shape: "
            "title, bullet points, and price. **Keep Data Private** sends it only to providers that do not store "
            "or train on requests.\n\n"
            "**List the Spec Facts** turns the spec sheet into plain facts. Jev compares them with the listing: "
            "**Supported** asks whether every claim is backed, and **Persuasive** scores the copy. The listing "
            "goes to `listings/approved` only when Jev finds every claim supported.\n\n"
            "Three paid requests per run. " + PRICES
        ),
    },
    "chat-02-caption-a-training-set": {
        "start": (
            KEY_STEP + "2. Choose a folder of images in **Training Images**.\n"
            "3. Press **Run**. **Save Captions** writes each image and its caption to `output/captions`."
        ),
        "using": (
            "**Caption Each Image** runs once per image, so a folder of 20 images sends 20 paid requests. Each "
            "caption is one sentence that names only what is visible.\n\n"
            "Jev then checks every caption in **Caption Rules**: one sentence, visible content only, no opinions. "
            "**Caption Verdicts** lists Jev's answer for each image, so you can fix the few that fail before "
            "training.\n\n" + PRICES
        ),
    },
    "image-01-pick-the-best-image-for-an-occasion": {
        "start": (
            KEY_STEP + "2. Describe the occasion in **Occasion Brief**.\n"
            "3. Press **Run**. Three image models draw a candidate each, and Jev picks one.\n"
            "4. The chosen image is saved under `occasion/approved`, or `occasion/review` when Jev is unsure."
        ),
        "using": (
            "**Candidate 1**, **Candidate 2**, and **Candidate 3** use three of the newest image models on the same "
            "brief. **Describe the Candidates** looks at all three in one request and describes each by number.\n\n"
            "Jev reads the brief and the descriptions. **Best Candidate** picks one, and its position chooses the "
            "image in **Chosen Image**. **Ready to Send** decides whether it can go to the client as it is.\n\n"
            "Five paid requests per run. " + PRICES
        ),
    },
    "image-02-reject-distorted-images": {
        "start": (
            KEY_STEP + "2. Describe the picture in **Subject**.\n"
            "3. Press **Run**. The draft is saved under `drafts/approved`, or `drafts/rejected` when Jev finds it "
            "distorted."
        ),
        "using": (
            "Two signals reach Jev, which reads text only. **Match a Clean Picture** and **Match a Distorted "
            "Picture** compare the draft with two descriptions using image embeddings; the second number in each "
            "is the draft's similarity. **Find Defects** lists what a vision model sees, such as extra fingers or "
            "garbled text.\n\n"
            "**Distorted** asks Jev for a yes or no from both signals. A run that fails the check can be retried "
            "with a new **seed** on **Draft**.\n\n"
            "Five paid requests per run. " + PRICES
        ),
    },
    "image-03-edit-with-the-best-idea": {
        "start": (
            KEY_STEP + "2. Upload the photo in **Product Photo** and describe the campaign in **Campaign**.\n"
            "3. Press **Run**. The edited image is saved under `campaign/approved` or `campaign/review`."
        ),
        "using": (
            "**Write Edit Ideas** looks at the photo and answers with three editing ideas as JSON. Jev picks the "
            "one that fits the campaign in **Best Idea**, and **Extract the Idea** passes its text to **Apply the "
            "Idea**, which edits the photo.\n\n"
            "**On Brief** asks Jev whether the chosen idea suits the campaign at all; when it does not, the result "
            "goes to `campaign/review`. **Chosen Idea** shows the instruction that was used.\n\n"
            "Three paid requests per run. " + PRICES
        ),
    },
    "image-04-design-a-logo": {
        "start": (
            KEY_STEP + "2. Describe the brand in **Brand Brief**.\n"
            "3. Press **Run**. The logo is saved as an SVG file and as a PNG sticker with a transparent background."
        ),
        "using": (
            "**Write Logo Prompts** answers with three prompts as JSON, and Jev picks the strongest in **Best "
            "Prompt**. **Vector Logo** draws it as SVG for **Save Logo**, and **Sticker** draws it on a "
            "transparent background.\n\n"
            "The picture and its transparency arrive separately: **Add Transparency** joins them, so the saved PNG "
            "keeps its transparent background. **Sticker Mask** shows the transparency; white marks the transparent "
            "area.\n\n"
            "Four paid requests per run. " + PRICES
        ),
    },
    "video-01-animate-a-product-shot": {
        "start": (
            KEY_STEP + "2. Describe the product shot in **Product Brief**.\n"
            "3. Press **Run**. The video is saved under `video/openrouter`."
        ),
        "using": (
            "**First Frame** draws a 16:9 still. **Write Camera Moves** looks at it and answers with three camera "
            "moves as JSON. Jev picks the one that suits a six-second teaser in **Best Move**, and **Animate** "
            "turns the still into video with that move.\n\n"
            "Video is the costly step and is billed per second; check the price in **OpenRouter models** first. "
            "If you cancel, the job keeps running and is billed; collect it with the **Video: Collect a Video** "
            "workflow.\n\n"
            "Four paid requests per run. " + PRICES
        ),
    },
    "video-02-collect-a-video": {
        "start": (
            "1. Choose the job in **Unfinished Job**. Press R in ComfyUI to list jobs recorded after the page "
            "loaded.\n"
            "2. Press **Run**. The video is saved under `video/openrouter`."
        ),
        "using": (
            "OpenRouter keeps making a video after a cancel, a restart, or a run that stopped waiting, and bills it. "
            "**Video: Generate** records every job it starts, and **Unfinished Job** lists them.\n\n"
            "Collecting a job sends only status and download requests, which bill nothing. The job leaves the list "
            "once its video is saved."
        ),
    },
    "audio-01-triage-a-voicemail": {
        "start": (
            KEY_STEP + "2. Upload the voicemail in **Voicemail**.\n"
            "3. Press **Run**. The transcript and a spoken callback script are saved under `voicemail`."
        ),
        "using": (
            "**Transcribe** turns the recording into text. Jev answers three questions about it: **Department** "
            "(one choice), **Call Back** (yes or no), and **Urgency** (a score). **Triage Summary** shows all "
            "three.\n\n"
            "**Write the Script** drafts what the chosen department says when it calls back, and **Speak the "
            "Script** reads it aloud. Calls that need a callback are saved under `voicemail/call-back`.\n\n"
            "Four paid requests per run. " + PRICES
        ),
    },
    "audio-02-dub-a-clip-in-your-voice": {
        "start": (
            KEY_STEP + "2. Upload a short clip of one speaker in **Your Clip**. The same clip is the voice sample.\n"
            "3. Press **Run**. The Spanish dub is saved under `dub/approved` or `dub/review`."
        ),
        "using": (
            "**Transcribe** writes the words and subtitles. **Translate** turns the words into Spanish, and Jev "
            "checks in **Faithful** that nothing was added or left out. **Speak in Your Voice** reads the "
            "translation in the voice of your clip, using its transcript as the sample text.\n\n"
            "Use a clip of your own voice, or one you have permission to copy. The subtitles are saved as text.\n\n"
            "Four paid requests per run. " + PRICES
        ),
    },
    "search-01-answer-from-help-articles": {
        "start": (
            KEY_STEP + "2. Type the customer's question in **Customer Question**, and your articles in **Help "
            "Articles**, one per line.\n"
            "3. Press **Run**. **Reply** shows the answer, or an escalation note."
        ),
        "using": (
            "**Find Relevant Articles** ranks every article against the question and keeps the best three. **Draft "
            "the Answer** answers from those three only.\n\n"
            "Jev checks the draft: **Supported** asks whether every sentence comes from the articles, and **Needs a "
            "Person** asks whether a person should handle it. An unsupported draft is replaced by an escalation "
            "note.\n\n"
            "Three paid requests per run. " + PRICES
        ),
    },
    "search-02-choose-a-hero-image": {
        "start": (
            KEY_STEP + "2. Describe the page and the picture you need in **Hero Brief**.\n"
            "3. Press **Run**. The best of four images is saved under `hero/approved` or `hero/review`."
        ),
        "using": (
            "**Four Candidates** draws four images in one request. **Rank the Images** scores each against the "
            "brief with a vision reranker and keeps the best.\n\n"
            "**Describe the Winner** writes what the winning image shows. Jev then decides in **Hero Ready** whether "
            "it works as a homepage hero: a clear subject, room for a headline, and no defects.\n\n"
            "Four paid requests per run. " + PRICES
        ),
    },
    "decision-01-verify-then-escalate": {
        "start": (
            KEY_STEP + "2. Paste your notes in **Notes** and type the question in **Question**.\n"
            "3. Press **Run**. **Answer** shows the cheap model's answer, or the strong model's when Jev doubts it."
        ),
        "using": (
            "**Quick Answer** uses a fast, inexpensive model. Jev checks in **Supported** that every fact in it "
            "comes from the notes, with a threshold of 0.8.\n\n"
            "**If/Else Switch** runs only the branch it picks, so **Careful Answer**, a stronger and dearer model, "
            "runs only when the quick answer fails the check.\n\n"
            "Two or three paid requests per run. " + PRICES
        ),
    },
}

__all__ = ["SHARED_TEXTS", "WORKFLOW_TEXTS"]
