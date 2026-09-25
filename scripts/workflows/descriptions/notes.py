"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.\n"

WORKFLOW_TEXTS = {
    "chat-01-write-a-product-listing": {
        "input": (
            KEY_STEP + "2. Upload a front photo in **Front** and a close-up in **Detail**.\n"
            "3. In **Chat: Attach Document**, choose the spec sheet: a PDF or text file in ComfyUI's input "
            "folder.\n"
            "4. Press **Run**. The listing is saved as JSON under `listings/approved` or `listings/review`.\n\n"
            "**Request Options** keeps the listing away from providers that store or train on requests."
        ),
        "write": (
            "GPT-6 Sol reads both photos and the spec sheet, and writes the listing as JSON: a title, five "
            "bullet points, and a price. GPT-6 Luna lists the facts in the spec sheet for **Check**.\n\n"
            "Open **Write** to change what each model is asked."
        ),
        "write_description": "Writes the listing from the photos and the spec sheet, and lists the spec's facts.",
        "check": (
            "Jev compares the listing with the spec facts and answers two questions: "
            "**supported** asks whether every claim is backed, and **persuasive** scores the copy.\n\n"
            "The listing is saved in the **approved** folder when every claim is supported, and in **review** "
            "otherwise."
        ),
        "check_description": "Asks Jev about the listing and saves it in the approved or review folder.",
    },
    "chat-02-caption-a-training-set": {
        "input": (
            KEY_STEP + "2. In **Load Image (from Folder)**, choose a folder of images in ComfyUI's input folder.\n"
            "3. Press **Run**. The captions are saved in `output/captions` as one JSON file, in image order."
        ),
        "caption": (
            "GPT-6 Luna reads every image in one request and writes one sentence for each that names only what "
            "is visible: the subject, setting, lighting, and style.\n\n"
            "Open **Caption** to change the instructions."
        ),
        "caption_description": "Writes one caption per image in one request and saves them as one JSON file.",
        "check": (
            "Jev reads the captions and answers **valid**: is every caption one "
            "sentence about visible content, without opinions or guesses?\n\n"
            "**Summary** gives the verdict, so you can fix the captions before training."
        ),
    },
    "image-01-pick-the-best-image-for-an-occasion": {
        "input": (
            KEY_STEP + "2. Describe the occasion in **Brief**: who it is for, the mood, and what to leave out.\n"
            "3. Press **Run**. The chosen image is saved under `occasion/approved`, or `occasion/review` when "
            "Jev finds a flaw."
        ),
        "draw": (
            "GPT Image 2.5 Flare, MAI-Image-2.6 Flash, and Recraft V4.1 Flash each draw one image from the "
            "brief. GPT-6 Luna then describes all three in one request, as candidate_1 to candidate_3, and names "
            "any flaw.\n\n"
            "Open **Draw** to change a model."
        ),
        "draw_description": "Draws one candidate with each of three models, and describes the three.",
        "choose": (
            "Jev reads the brief and the descriptions. **best** picks a candidate, and its position selects the "
            "image to save. **ready** asks whether it can go to the client as it is.\n\n"
            "The image is saved in the **approved** folder when Jev says it is ready, and in **review** "
            "otherwise."
        ),
        "choose_description": "Asks Jev for the best candidate and saves it in the approved or review folder.",
    },
    "image-02-reject-distorted-images": {
        "input": (
            KEY_STEP + "2. Describe the picture in **Subject**.\n"
            "3. Press **Run**. The draft is saved under `drafts/approved`, or `drafts/rejected` when Jev finds it "
            "distorted."
        ),
        "draw": ("MAI-Image-2.6 Flash draws the subject at 4:3. For another draft, change **seed** and run again."),
        "inspect": (
            "Jev reads text only, so this step describes the draft in numbers and words. Gemini Embedding 2 "
            "scores how close the draft is to a clean description and to a distorted one; the second number of "
            "each pair is the draft's. GPT-6 Luna lists any visible defect, such as extra fingers or garbled "
            "text."
        ),
        "inspect_description": "Scores the draft against a clean and a distorted description, and lists defects.",
        "check": (
            "Jev weighs the scores and the defects and answers **distorted**. The draft is saved in the "
            "**rejected** folder when it is distorted, and in **approved** otherwise."
        ),
        "check_description": "Asks Jev whether the draft is distorted and saves it in the approved or rejected folder.",
    },
    "image-03-edit-with-the-best-idea": {
        "input": (
            KEY_STEP + "2. Upload the product photo in **Load Image**, and describe the campaign in **Campaign**.\n"
            "3. Press **Run**. The edited photo is saved under `campaign/approved` or `campaign/review`."
        ),
        "ideas": (
            "GPT-6 Sol looks at the photo and writes three ideas for editing it into a campaign image, as idea_1 "
            "to idea_3. Each idea keeps the product exactly as it is."
        ),
        "ideas_description": "Writes three editing ideas for the photo.",
        "choose": (
            "Jev reads the campaign and the ideas. **best** picks one, and "
            "**on_brief** asks whether it suits the campaign at all. **Idea** shows the chosen instruction."
        ),
        "choose_description": "Asks Jev for the best idea and whether it suits the campaign.",
        "edit": (
            "GPT Image 2.5 Flare edits the photo with the chosen idea, keeping the photo as its reference. The "
            "result is saved in the **approved** folder when the idea is on brief, and in **review** otherwise."
        ),
        "edit_description": "Edits the photo with the chosen idea and saves it in the approved or review folder.",
    },
    "image-04-design-a-logo": {
        "input": (
            KEY_STEP + "2. Describe the brand in **Brand**: its name, its character, and where the logo is used.\n"
            "3. Press **Run**. The logo is saved under `logo` as an SVG file and as a PNG with a transparent "
            "background.\n\n"
            "To draw the PNG with another model, change **Model**."
        ),
        "prompts": (
            "GPT-6 Sol writes three logo prompts, as prompt_1 to prompt_3. Jev picks "
            "the one that will make the simplest, most memorable mark in **best**, and **Prompt** shows it."
        ),
        "prompts_description": "Writes three logo prompts and asks Jev for the best one.",
        "svg": "Recraft V4.1 Vector draws the prompt as an SVG file, which scales to any size without blurring.",
        "svg_description": "Draws the logo as SVG and saves it.",
        "png": (
            "GPT Image 2.5 Flare draws the prompt on a transparent background. The picture and its transparency "
            "arrive separately, so **Join Image with Alpha** puts them together before saving. **Mask** shows "
            "the transparency; white marks the transparent area."
        ),
        "png_description": "Draws the logo on a transparent background and saves it as a PNG.",
        "model": (
            "**Model** holds the model **PNG** draws with. **Model: Info** reads what OpenRouter lists for it, "
            "for free and without the key, and **Info** shows it: the aspect ratios, qualities, and "
            "backgrounds it takes. Change the model here, and check **Info** before you change **PNG**'s "
            "settings."
        ),
    },
    "video-01-animate-a-product-shot": {
        "input": (
            KEY_STEP + "2. Describe the shot in **Brief**.\n"
            "3. Press **Run**. The video is saved under `video/openrouter`.\n\n"
            "To animate with another video model, change **Model**."
        ),
        "frame": (
            "MAI-Image-2.6 Flash draws the first frame at 16:9, and **Frame** shows it. For another frame, "
            "change **seed** and run again."
        ),
        "move": (
            "GPT-6 Sol looks at the frame and writes three camera moves, as move_1 to move_3. Jev picks the one "
            "that best suits a six-second teaser in **best**, and **Move** shows it."
        ),
        "move_description": "Writes three camera moves for the frame and asks Jev for the best one.",
        "animate": (
            "MiniMax H3 Max turns the frame into a six-second 768p video with the chosen move. If you cancel, "
            "OpenRouter still makes the video; download it with **video-02-recover-a-cancelled-video**."
        ),
        "animate_description": "Turns the frame into a video with the chosen move and saves it.",
        "model": (
            "**Model** holds the video model **Animate** uses. **Model: Info** reads what OpenRouter lists for "
            "it, for free and without the key, and **Info** shows it: the durations, resolutions, and aspect "
            "ratios it takes. Change the model here, and check **Info** before you change **Animate**'s "
            "settings."
        ),
    },
    "video-02-recover-a-cancelled-video": {
        "recover": (
            "Use this after you cancel a run of **Video: Generate**, or after ComfyUI restarts while a video is "
            "being made. OpenRouter still makes the video.\n\n"
            "1. In **job**, choose the video. Each entry shows its ID, model, and start time. Press R to list "
            "jobs started after the page loaded.\n"
            "2. Press **Run**. The video is saved under `video/openrouter`.\n\n"
            "A job leaves the list once its video is saved."
        ),
    },
    "audio-01-triage-a-voicemail": {
        "input": (
            KEY_STEP + "2. Upload the voicemail in **Load Audio**.\n"
            "3. Press **Run**. The transcript and a spoken reply are saved under `voicemail`."
        ),
        "transcribe": (
            "Universal-3.5 Pro turns the recording into text, and the transcript is saved under `voicemail/transcript`."
        ),
        "transcribe_description": "Transcribes the recording and saves the transcript.",
        "triage": (
            "Jev reads the transcript and answers three questions: **department** "
            "picks sales, support, or billing; **callback** asks whether the caller wants a call back; "
            "**urgency** scores how soon. **Summary** shows all three."
        ),
        "triage_description": "Asks Jev which department replies, whether to call back, and how soon.",
        "reply": (
            "GPT-6 Luna writes what the chosen department says when it calls back, and Gemini 3.8 Flash TTS "
            "reads it aloud. The reply is saved under `voicemail/reply`."
        ),
        "reply_description": "Writes the department's reply, speaks it, and saves it.",
    },
    "audio-02-dub-a-clip": {
        "input": (
            KEY_STEP
            + "2. Upload a short clip of one speaker in **Load Audio**. The clip is also the voice sample, so use "
            "your own voice or one you have permission to copy.\n"
            "3. Press **Run**. The dub is saved under `dub/approved` or `dub/review`, and the subtitles under "
            "`dub/subtitles`."
        ),
        "transcribe": ("Universal-3.5 Pro turns the clip into text, and saves timed subtitles under `dub/subtitles`."),
        "transcribe_description": "Transcribes the clip and saves its subtitles.",
        "translate": (
            "GPT-6 Sol translates the transcript into the **language** on **Translate**. Jev compares the two and "
            "answers **accurate**: does the translation say the same, with nothing added or left out?"
        ),
        "translate_description": "Translates the transcript and asks Jev whether the translation is accurate.",
        "speak": (
            "Fish Audio S2.1 Pro reads the translation in the voice of the clip, using the transcript as the "
            "sample text. The dub is saved in the **approved** folder when the translation is accurate, and in "
            "**review** otherwise."
        ),
        "speak_description": "Speaks the translation in the clip's voice and saves it by Jev's verdict.",
    },
    "search-01-answer-from-help-articles": {
        "input": (
            KEY_STEP
            + "2. Type the customer's question in **Question**, and your help articles in **Articles**, one per "
            "line.\n"
            "3. Press **Run**. **Reply** shows the answer, or a note to pass the customer to a person."
        ),
        "search": (
            "Rerank 4 Pro scores every article against the question and keeps the best three, set in **top n**."
        ),
        "answer": (
            "GPT-6 Luna answers the customer in three sentences or fewer, using only the three articles. Open "
            "**Answer** to change the instructions."
        ),
        "answer_description": "Answers the customer from the ranked articles.",
        "check": (
            "Jev reads the articles and the answer and answers **supported**: does "
            "every sentence come from the articles? When it does, **Reply** shows the answer; when it does not, "
            "a note to pass the customer to a person."
        ),
        "check_description": "Asks Jev whether the answer is supported, and returns it or a note to escalate.",
    },
    "search-02-choose-a-hero-image": {
        "input": (
            KEY_STEP + "2. Describe the page and the picture you need in **Brief**.\n"
            "3. Press **Run**. The best of four images is saved under `hero/approved` or `hero/review`."
        ),
        "rank": (
            "Recraft V4.1 Flash draws four images in one request. Llama Nemotron Rerank VL, a vision reranker, "
            "scores each against the brief and keeps the best."
        ),
        "rank_description": "Draws four candidates and keeps the one that best matches the brief.",
        "check": (
            "GPT-6 Luna describes the winner. Jev then answers **ready**: does it "
            "work as a homepage hero, with a clear subject, room for a headline, and no defects? The image is "
            "saved in the **approved** folder when it is ready, and in **review** otherwise."
        ),
        "check_description": "Asks Jev whether the winner works as a hero and saves it by the verdict.",
    },
    "decision-01-verify-then-escalate": {
        "input": (
            KEY_STEP + "2. Paste your notes in **Notes** and type the question in **Question**.\n"
            "3. Press **Run**. **Answer** shows the quick answer, or the careful one when Jev doubts it."
        ),
        "answer": "GPT-6 Luna, a fast model, answers the question using only the notes.",
        "answer_description": "Answers the question from the notes with a fast model.",
        "check": (
            "Jev answers **supported**: does every fact in the answer come from the notes? The answer passes "
            "when the probability of yes is at least 0.8."
        ),
        "check_description": "Asks Jev whether every fact in the answer comes from the notes.",
        "escalate": (
            "When the quick answer fails the check, Claude Opus 5.5 answers again with more care. **If/Else "
            "Switch** runs only the branch it picks, so the stronger model runs only when the quick answer fails."
        ),
        "escalate_description": "Asks a stronger model only when the quick answer fails the check.",
    },
}

__all__ = ["WORKFLOW_TEXTS"]
