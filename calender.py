from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from pathlib import Path
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from dateutil import parser
import datetime
import time
import psutil

# TODO 
# 1. Determine if a new token is needed - then promt to run a -t version to generate new token
# 2. Fix flickering - terminal maybe
# 3. Take photos to upload to github! 
# 4. create todos with events and block untill day of?

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]
BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / 'token.json'

console = Console()

def auth_google():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            BASE_DIR / 'client-secret.json', SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory()
    mem_used = mem.used // (1024 * 1024)
    mem_total = mem.total // (1024 * 1024)
    mem_percent = mem.percent

    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = int(f.read().strip()) / 1000
    except:
        temp_c = None

    return cpu_percent, mem_used, mem_total, mem_percent, temp_c

def fetch_events(service):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=15, singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def fetch_tasks(creds):
    service = build('tasks', 'v1', credentials=creds)
    tasklists = service.tasklists().list().execute()

    all_tasks = []

    for tasklist in tasklists['items']:
        tasks = service.tasks().list(tasklist=tasklist['id']).execute()
        for task in tasks.get('items', []):
            all_tasks.append((task.get('title'), task.get('due')))

    return all_tasks

def split_events(events):
    today = []
    tasks = []
    upcoming = []
    now = datetime.datetime.now().astimezone()

    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        try:
            start = parser.isoparse(start_str).astimezone()
        except (ValueError, TypeError):
            continue

        summary = event.get('summary', 'No Title')
        is_all_day = 'date' in event['start'] and 'dateTime' not in event['start']

        if start.date() == now.date():
            if is_all_day:
                tasks.append((start, summary))
            else:
                today.append((start, summary))
        elif start > now:
            upcoming.append((start, summary))

    return today, upcoming, tasks

def render_sysinfo_page(page_num, total_pages, countdown):
    cpu, used, total, mem_percent, temp = get_system_info()

    lines = [
        Text("System Info", style="bold cyan", justify="center"),
        Text(f"CPU Usage: {cpu:.1f}%"),
        Text(f"RAM Usage: {used}MB / {total}MB ({mem_percent:.1f}%)"),
    ]
    if temp is not None:
        lines.append(Text(f"Temperature: {temp:.1f}°C"))

    footer = Text(f"Page {page_num}/{total_pages} | Next in {countdown:02}s", style="dim", justify="center")

    layout = Layout()
    layout.split_column(
        Layout(make_header("System Info"), name="header", size=1),
        Layout(Panel(Group(*lines[1:]), padding=(0, 1), border_style="cyan"), name="body"),
        Layout(Align.center(footer), name="footer", size=1)
    )

    return layout

def make_header(title) -> Layout:
    now = datetime.datetime.now().strftime("%-I:%M %p")
    header_layout = Layout()
    header_layout.split_row(
        Layout(Text(title, style="bold cyan"), name="title"),
        Layout(Align.right(Text(now, style="bold green")), name="clock", ratio=1)
    )
    return header_layout

def render_page(title, events, page_num, total_pages, countdown, tasks=[]):
    header = Text(title, style="bold cyan", justify="left")
    now_str = datetime.datetime.now().strftime("%-I:%M %p")
    clock = Text(now_str, style="bold yellow")
    header_line = Text.assemble(header, " " * (console.width - len(header.plain) - len(clock.plain) - 2), clock)

    body_lines = []
    today = datetime.datetime.now().date()
    week_end = today + datetime.timedelta(days=6 - today.weekday())  # end of week (sunday)

    for start, summary in events[:5]:
        start_date = start.date()
        if start_date == today:
            time_str = start.strftime('%-I:%M %p')  # today
        elif today < start_date <= week_end:
            time_str = start.strftime('%a')         # this week
        else:
            time_str = start.strftime('%b %-d')      # not this week, show date

        line = Text(f"{time_str} {summary}")
        line.truncate(console.width - 4, overflow="ellipsis")
        line.no_wrap = True
        body_lines.append(line)
        
    if tasks:
        body_lines.append(Text(""))
        body_lines.append(Text("Tasks:", style="bold magenta"))
        for _, summary in tasks[:5]:  # limit og 5
            line = Text(f"• {summary}")
            line.truncate(console.width - 4, overflow="ellipsis")
            line.no_wrap = True
            body_lines.append(line)

    if len(events) > 5:
        body_lines.append(Text(f"+{len(events) - 5} more...", style="dim"))
    if len(tasks) > 3:
        body_lines.append(Text(f"+{len(tasks) - 3} more tasks...", style="dim"))

    footer_text = Text(f"Page {page_num}/{total_pages} | Next in {countdown:02}s", style="dim", justify="center")

    layout = Layout()
    layout.split_column(
        Layout(Align.center(header_line), name="header", size=1),
        Layout(Panel(Group(*body_lines), padding=(0, 1), border_style="cyan"), name="body"),
        Layout(Align.center(footer_text), name="footer", size=1)
    )

    return layout

if __name__ == '__main__':
    creds = auth_google()
    calendar_service = build('calendar', 'v3', credentials=creds)
    tasks_service = build('tasks', 'v1', credentials=creds)

    fetch_interval = 3 * 60  # seconds between fetches
    display_interval = 60     # seconds per page
    last_fetch = 0

    with Live(console=console, refresh_per_second=1, screen=False) as live:
        while True:
            now = time.time()
            if now - last_fetch > fetch_interval:
                all_events = fetch_events(calendar_service)
                today, upcoming, calendar_tasks = split_events(all_events)

                all_tasks = fetch_tasks(creds)
                today_str = datetime.datetime.now().date().isoformat()
                tasks_today = [
                    (parser.isoparse(due).astimezone(), title)
                    for title, due in all_tasks if due and parser.isoparse(due).date().isoformat() == today_str
                ]

                last_fetch = now
            else:
                tasks_today = tasks_today if 'tasks_today' in locals() else []

            pages = [
                ("Today", today, tasks_today + calendar_tasks),
                ("Upcoming", upcoming, []),
                ("System Info", [], [])
            ]

            last_panel = None
            for idx, (title, evs, tasks) in enumerate(pages, 1):
                for countdown in range(display_interval, 0, -1):
                    if title == "System Info":
                        panel = render_sysinfo_page(idx, len(pages), countdown)
                    else:
                        panel = render_page(title, evs, idx, len(pages), countdown, tasks)
                    if panel != last_panel:
                        live.update(panel)
                        last_panel = panel
                    time.sleep(1)