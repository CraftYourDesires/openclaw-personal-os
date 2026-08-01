from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "remm-personal-os-call-overview.pdf"
ART = ROOT / "guide" / "assets" / "personal-os-command-center.png"

PAGE_W, PAGE_H = landscape(letter)
NAVY = HexColor("#12263A")
INK = HexColor("#17202A")
CREAM = HexColor("#F7F3EA")
PAPER = HexColor("#FFFDFC")
MINT = HexColor("#91D8C5")
MINT_PALE = HexColor("#E6F6F1")
CORAL = HexColor("#FF7E6B")
CORAL_PALE = HexColor("#FFE8E3")
BLUE = HexColor("#6DA9E4")
BLUE_PALE = HexColor("#E8F2FB")
GOLD = HexColor("#F2C14E")
GRAY = HexColor("#5E6B75")
LINE = HexColor("#D9E1E5")


def wrap(text, font, size, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if not current or stringWidth(trial, font, size) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(c, text, x, y, width, font="Helvetica", size=16, color=INK, leading=None, max_lines=None):
    leading = leading or size * 1.28
    lines = wrap(text, font, size, width)
    if max_lines:
        lines = lines[:max_lines]
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def footer(c, page_num):
    c.setStrokeColor(LINE)
    c.line(40, 30, PAGE_W - 40, 30)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(GRAY)
    c.drawString(40, 17, "OPENCLAW PERSONAL OS  |  CALL OVERVIEW")
    c.drawRightString(PAGE_W - 40, 17, f"{page_num:02d}")


def page_header(c, section, title, subtitle, page_num):
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.roundRect(40, PAGE_H - 64, 122, 24, 12, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(101, PAGE_H - 56, section.upper())
    c.setFont("Helvetica-Bold", 29)
    c.drawString(40, PAGE_H - 105, title)
    text_block(c, subtitle, 40, PAGE_H - 131, PAGE_W - 80, size=13, color=GRAY, leading=17)
    footer(c, page_num)


def card(c, x, y, w, h, title, body, fill=CREAM, accent=MINT, number=None, title_size=15, body_size=11.5):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 16, fill=1, stroke=0)
    c.setFillColor(accent)
    c.roundRect(x, y + h - 8, w, 8, 4, fill=1, stroke=0)
    title_x = x + 18
    if number is not None:
        c.setFillColor(accent)
        c.circle(x + 28, y + h - 34, 14, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 28, y + h - 38, str(number))
        title_x = x + 50
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", title_size)
    c.drawString(title_x, y + h - 40, title)
    text_block(c, body, x + 18, y + h - 65, w - 36, size=body_size, color=INK, leading=body_size * 1.34)


def bullet_list(c, items, x, y, width, color=INK, size=13, gap=10, dot=MINT):
    for item in items:
        c.setFillColor(dot)
        c.circle(x + 5, y + 4, 4, fill=1, stroke=0)
        lines = wrap(item, "Helvetica", size, width - 22)
        c.setFillColor(color)
        c.setFont("Helvetica", size)
        line_y = y
        for line in lines:
            c.drawString(x + 20, line_y, line)
            line_y -= size * 1.3
        y = line_y - gap
    return y


def prompt_bubble(c, text, x, y, w, accent):
    lines = wrap(text, "Helvetica-Bold", 13, w - 38)
    h = 32 + len(lines) * 17
    c.setFillColor(white)
    c.setStrokeColor(accent)
    c.setLineWidth(2)
    c.roundRect(x, y - h, w, h, 18, fill=1, stroke=1)
    c.setFillColor(accent)
    c.circle(x + 19, y - 24, 7, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    line_y = y - 29
    for line in lines:
        c.drawString(x + 36, line_y, line)
        line_y -= 17
    return y - h


def arrow(c, x1, y1, x2, y2, color=BLUE):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(3)
    c.line(x1, y1, x2, y2)
    c.line(x2, y2, x2 - 8, y2 + 5)
    c.line(x2, y2, x2 - 8, y2 - 5)


def draw_cover(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.circle(75, PAGE_H - 70, 11, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(white)
    c.drawString(96, PAGE_H - 74, "A QUICK GUIDE FOR YOUR CALL WITH REMM")
    c.setFont("Helvetica-Bold", 38)
    c.drawString(48, PAGE_H - 150, "Remm's OpenClaw")
    c.drawString(48, PAGE_H - 197, "Personal OS")
    text_block(c, "What you built, how it works, and how Remm gets from zero to a verified personal AI system.", 50, PAGE_H - 235, 350, size=16, color=HexColor("#DDE9EF"), leading=22)
    for label, x, color in [("SPEAK", 50, MINT), ("ORGANIZE", 135, CORAL), ("REMEMBER", 245, GOLD), ("BUILD", 365, BLUE)]:
        c.setFillColor(color)
        c.roundRect(x, 78, 76 if label != "ORGANIZE" else 98, 28, 14, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + (38 if label != "ORGANIZE" else 49), 88, label)
    if ART.exists():
        img = ImageReader(str(ART))
        c.saveState()
        clip_x, clip_y, clip_w, clip_h = 435, 92, 315, 402
        path = c.beginPath()
        path.roundRect(clip_x, clip_y, clip_w, clip_h, 22)
        c.clipPath(path, stroke=0, fill=0)
        c.drawImage(img, clip_x, clip_y, width=clip_w, height=clip_h, preserveAspectRatio=False, mask="auto")
        c.restoreState()
        c.setStrokeColor(MINT)
        c.setLineWidth(4)
        c.roundRect(435, 92, 315, 402, 22, fill=0, stroke=1)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#BFD0D8"))
    c.drawString(50, 40, "CraftYourDesires/openclaw-personal-os")


def draw_map(c, page_num):
    page_header(c, "System map", "One voice, one private doorway, one memory", "The system turns natural speech and meetings into reviewed tasks, calendar events, and durable knowledge.", page_num)
    nodes = [
        (46, 314, 118, 72, "Wispr Flow", "Speak naturally", MINT_PALE, MINT),
        (198, 314, 118, 72, "Telegram", "Private doorway", BLUE_PALE, BLUE),
        (350, 294, 152, 112, "OpenClaw", "Routes the request", CORAL_PALE, CORAL),
        (536, 314, 118, 72, "Codex", "Reasons and acts", MINT_PALE, MINT),
        (688, 314, 62, 72, "Done", "", CREAM, GOLD),
    ]
    for x, y, w, h, title, body, fill, accent in nodes:
        c.setFillColor(fill)
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        c.roundRect(x, y, w, h, 16, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14 if w > 70 else 12)
        c.drawCentredString(x + w / 2, y + h - 28, title)
        if body:
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 9.5)
            c.drawCentredString(x + w / 2, y + 22, body)
    for start, end in [(164, 198), (316, 350), (502, 536), (654, 688)]:
        arrow(c, start + 4, 350, end - 4, 350)
    card(c, 78, 114, 190, 118, "Obsidian", "Daily notes, tasks, calendar context, meeting records, and long term memory.", fill=MINT_PALE, accent=MINT)
    card(c, 302, 114, 190, 118, "Granola", "Meeting transcripts flow into a review packet before actions become tasks.", fill=CORAL_PALE, accent=CORAL)
    card(c, 526, 114, 190, 118, "Google + Projects", "Two calendars, GitHub projects, and Vercel deployments stay connected.", fill=BLUE_PALE, accent=BLUE)
    c.setStrokeColor(LINE)
    c.setLineWidth(2)
    c.line(426, 294, 426, 252)
    c.line(173, 252, 621, 252)
    for x in [173, 397, 621]:
        c.line(x, 252, x, 232)


def draw_section_one(c, page_num):
    page_header(c, "1", "Explain it in one minute", "Use this language first. Details can wait until Remm understands the outcome.", page_num)
    c.setFillColor(NAVY)
    c.roundRect(40, 287, 712, 175, 24, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 48)
    c.drawString(65, 398, '"')
    quote = "You speak normally. OpenClaw and Codex organize the request. Obsidian remembers it. Granola captures the meeting. You stay in control of what becomes real."
    text_block(c, quote, 95, 409, 610, font="Helvetica-Bold", size=20, color=white, leading=28)
    card(c, 40, 92, 166, 150, "Speak", "Wispr Flow makes Telegram feel conversational.", fill=MINT_PALE, accent=MINT)
    card(c, 222, 92, 166, 150, "Organize", "Tasks, reminders, recurring work, and events land in the right place.", fill=CORAL_PALE, accent=CORAL)
    card(c, 404, 92, 166, 150, "Remember", "Notes and meetings become searchable personal context.", fill=BLUE_PALE, accent=BLUE)
    card(c, 586, 92, 166, 150, "Build", "Codex can create projects through GitHub and Vercel.", fill=CREAM, accent=GOLD)


def draw_section_two(c, page_num):
    page_header(c, "2", "Show what it can do", "Read these examples aloud. They make the system concrete without explaining technical details.", page_num)
    y_left = 442
    y_left = prompt_bubble(c, "Remind me every Wednesday at nine to prepare the weekly update.", 42, y_left, 340, MINT) - 18
    y_left = prompt_bubble(c, "Add a task to send Sarah the proposal by Friday.", 42, y_left, 340, CORAL) - 18
    prompt_bubble(c, "Put lunch with Alex on my calendar next Tuesday at one.", 42, y_left, 340, BLUE)
    y_right = 442
    y_right = prompt_bubble(c, "What did we decide in my last marketing meeting?", 410, y_right, 340, GOLD) - 18
    y_right = prompt_bubble(c, "What do I still owe people across my notes and meetings?", 410, y_right, 340, MINT) - 18
    prompt_bubble(c, "Build a simple project tracker and publish it for me.", 410, y_right, 340, CORAL)


def draw_section_three(c, page_num):
    page_header(c, "3", "Meetings become reviewed follow through", "Granola captures the conversation. Codex proposes the actions. Remm decides what becomes a task.", page_num)
    steps = [
        ("Granola", "Records and transcribes the meeting."),
        ("Obsidian", "Stores the full transcript and meeting note."),
        ("Codex", "Finds possible actions, owners, and dates."),
        ("Remm approves", "Only selected actions become TaskNotes."),
    ]
    x = 42
    for i, (title, body) in enumerate(steps, 1):
        card(c, x, 246, 165, 180, title, body, fill=[MINT_PALE, BLUE_PALE, CORAL_PALE, CREAM][i - 1], accent=[MINT, BLUE, CORAL, GOLD][i - 1], number=i)
        if i < 4:
            arrow(c, x + 169, 336, x + 185, 336, color=GRAY)
        x += 181
    c.setFillColor(NAVY)
    c.roundRect(42, 92, 708, 112, 20, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(65, 160, "The trust rule")
    text_block(c, "A transcript can contain guesses, tentative ideas, and work assigned to someone else. That is why meeting actions stay proposed until Remm explicitly approves them.", 65, 134, 640, size=14, color=white, leading=20)


def draw_section_four(c, page_num):
    page_header(c, "4", "One daily command center", "Each morning, one Obsidian note brings the day together.", page_num)
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.setLineWidth(2)
    c.roundRect(42, 86, 400, 370, 20, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(66, 416, "Friday, August 1")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 10)
    c.drawString(66, 395, "Your day, assembled automatically")
    sections = [
        ("TOP PRIORITIES", ["Prepare weekly update", "Send Sarah the proposal"]),
        ("CALENDAR", ["10:00 Team planning", "1:00 Lunch with Alex"]),
        ("MEETING FOLLOW THROUGH", ["Review two proposed Granola actions"]),
    ]
    y = 356
    for label, items in sections:
        c.setFillColor(MINT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(66, y, label)
        y -= 24
        for item in items:
            c.setStrokeColor(LINE)
            c.rect(68, y - 1, 12, 12, fill=0, stroke=1)
            c.setFillColor(INK)
            c.setFont("Helvetica", 12)
            c.drawString(92, y, item)
            y -= 27
        y -= 10
    card(c, 474, 330, 276, 126, "Tasks", "Today, overdue, recurring, and approved meeting actions appear together.", fill=MINT_PALE, accent=MINT)
    card(c, 474, 191, 276, 126, "Events", "Personal and work calendar context appears beside the work.", fill=BLUE_PALE, accent=BLUE)
    card(c, 474, 52, 276, 126, "Notes", "Remm can write freely without losing the structure around the day.", fill=CORAL_PALE, accent=CORAL)


def draw_section_five(c, page_num):
    page_header(c, "5", "Private by default", "The setup is useful because it has clear boundaries, not unlimited control of the Mac.", page_num)
    c.setFillColor(NAVY)
    c.circle(178, 275, 125, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.circle(178, 293, 45, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(178, 284, "PRIVATE")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(178, 215, "REMM OWNS")
    c.drawCentredString(178, 196, "EVERY ACCOUNT")
    items = [
        "Telegram accepts Remm's numeric user ID only.",
        "Groups are disabled initially.",
        "Tokens and secrets live in Doppler, never GitHub.",
        "Supported high risk actions require a short lived PIN.",
        "Meeting actions require review before task creation.",
        "Remm uses his own Google, GitHub, and Vercel accounts.",
    ]
    bullet_list(c, items, 345, 420, 395, size=14, gap=13, dot=CORAL)
    c.setFillColor(CORAL_PALE)
    c.roundRect(345, 80, 395, 76, 16, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(365, 127, "Do not connect his system using your accounts or tokens.")
    text_block(c, "The template is shared. The identity, data, and deployments belong to Remm.", 365, 106, 350, size=11.5, color=INK)


def draw_section_six(c, page_num):
    page_header(c, "6", "What Remm needs before setup", "The overview works today. Save this checklist for the installation session.", page_num)
    card(c, 42, 310, 220, 150, "Mac", "A personal MacBook, charger, internet connection, administrator password, and 60 to 90 minutes.", fill=MINT_PALE, accent=MINT)
    card(c, 286, 310, 220, 150, "Phone", "An iPhone with Telegram and access to the email accounts used for sign in confirmations.", fill=BLUE_PALE, accent=BLUE)
    card(c, 530, 310, 220, 150, "Accounts", "Paid ChatGPT, personal Google, work Google, and the ability to create the remaining accounts.", fill=CORAL_PALE, accent=CORAL)
    c.setFillColor(NAVY)
    c.roundRect(42, 92, 708, 174, 20, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(66, 226, "Accounts used during setup")
    accounts = ["ChatGPT with Codex", "GitHub", "Vercel", "Doppler", "Telegram", "Google", "Granola", "Wispr Flow", "Obsidian Sync"]
    for i, account in enumerate(accounts):
        col = i % 3
        row = i // 3
        x = 66 + col * 220
        y = 188 - row * 42
        c.setFillColor(white)
        c.circle(x + 7, y + 4, 6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 24, y, account)


def draw_section_seven(c, page_num):
    page_header(c, "7", "Start with one Codex prompt", "Codex performs the safe technical work and pauses when Remm must personally participate.", page_num)
    card(c, 42, 306, 210, 148, "1. Install Codex", "Install the Codex desktop app and sign in using Remm's paid ChatGPT account.", fill=MINT_PALE, accent=MINT)
    card(c, 291, 306, 210, 148, "2. Share the repository", "Give Codex the public repository link and ask it to clone the project locally.", fill=BLUE_PALE, accent=BLUE)
    card(c, 540, 306, 210, 148, "3. Paste the prompt", "Use the master prompt from the guide. Codex reads the files before installing anything.", fill=CORAL_PALE, accent=CORAL)
    c.setFillColor(NAVY)
    c.roundRect(42, 66, 708, 200, 20, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(64, 234, "COPY INTO CODEX")
    prompt = (
        "Set up my OpenClaw Personal OS using https://github.com/CraftYourDesires/"
        "openclaw-personal-os. Read README.md, DECISIONS.md, setup.sh, and guide/index.html first. "
        "Walk me through one step at a time. Perform safe setup work yourself. Pause only when I must "
        "sign in, approve permission, create a private token, choose a plan, or make a meaningful decision. "
        "Use my own accounts, store secrets through Doppler, preserve existing files, and continue until every "
        "required doctor check and controlled test passes."
    )
    text_block(c, prompt, 64, 207, 663, font="Helvetica", size=12.2, color=white, leading=17)


def draw_section_eight(c, page_num):
    page_header(c, "8", "Remm handles the personal sign ins", "Codex installs and verifies the technical pieces. Remm owns the identity and permission steps.", page_num)
    items = [
        ("Codex", "Sign in with paid ChatGPT"),
        ("GitHub + Vercel", "Create and own project accounts"),
        ("Doppler", "Create the private secrets project"),
        ("Telegram", "Create a bot with BotFather"),
        ("Wispr Flow", "Allow microphone and accessibility"),
        ("Obsidian", "Connect the personal Sync vault"),
        ("Google", "Authorize personal and work calendars"),
        ("Granola", "Sign in and permit meeting capture"),
    ]
    for i, (title, body) in enumerate(items):
        col = i % 2
        row = i // 2
        x = 42 + col * 363
        y = 392 - row * 74
        c.setFillColor([MINT, BLUE, CORAL, GOLD][row])
        c.circle(x + 21, y + 18, 20, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 21, y + 14, str(i + 1))
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 54, y + 26, title)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 11.5)
        c.drawString(x + 54, y + 7, body)
    c.setFillColor(MINT_PALE)
    c.roundRect(42, 62, 708, 64, 15, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(396, 89, "Remm should never paste private tokens into GitHub, source files, or documentation.")


def draw_section_nine(c, page_num):
    page_header(c, "9", "Done means proven", "The installation is complete only when the full loop works with Remm's own accounts.", page_num)
    checks = [
        ("Voice", "Wispr dictation reaches the private Telegram bot."),
        ("Recurring task", "A Wednesday request creates the correct schedule."),
        ("Calendar", "An event appears in the intended Google calendar."),
        ("Daily note", "Tasks and events appear in today's Obsidian note."),
        ("Granola", "A real transcript reaches the meeting review packet."),
        ("Approval", "Only selected meeting actions become tasks."),
        ("Recall", "A question returns evidence from real notes."),
        ("Build", "GitHub and Vercel publish the sample status page."),
    ]
    for i, (title, body) in enumerate(checks):
        col = i % 2
        row = i // 2
        x = 42 + col * 363
        y = 390 - row * 84
        c.setFillColor(MINT_PALE if col == 0 else BLUE_PALE)
        c.roundRect(x, y, 345, 67, 14, fill=1, stroke=0)
        c.setFillColor(MINT if col == 0 else BLUE)
        c.circle(x + 25, y + 34, 13, fill=1, stroke=0)
        c.setStrokeColor(NAVY)
        c.setLineWidth(2)
        c.line(x + 19, y + 34, x + 24, y + 29)
        c.line(x + 24, y + 29, x + 32, y + 39)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(x + 49, y + 40, title)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 10.5)
        c.drawString(x + 49, y + 21, body)
    c.setFillColor(NAVY)
    c.roundRect(42, 55, 708, 68, 16, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(396, 92, "For today's call, the overview is enough.")
    c.setFillColor(white)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(396, 72, "Send the guide and repository afterward, then schedule the installation session.")


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("Remm OpenClaw Personal OS Call Overview")
    c.setAuthor("Craft Your Desires")
    c.setSubject("A presenter guide for explaining and setting up Remm's OpenClaw Personal OS")
    draw_cover(c)
    c.showPage()
    draw_map(c, 2)
    c.showPage()
    draw_section_one(c, 3)
    c.showPage()
    draw_section_two(c, 4)
    c.showPage()
    draw_section_three(c, 5)
    c.showPage()
    draw_section_four(c, 6)
    c.showPage()
    draw_section_five(c, 7)
    c.showPage()
    draw_section_six(c, 8)
    c.showPage()
    draw_section_seven(c, 9)
    c.showPage()
    draw_section_eight(c, 10)
    c.showPage()
    draw_section_nine(c, 11)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
