import json
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen


LINKS_FILE = Path("links.txt")
OUT_FILE = Path("data/threads.json")


@dataclass
class Message:
    id: Optional[str]
    author: Optional[str]
    published: Optional[str]
    subject: Optional[str]
    text: str
    source: str


@dataclass
class ThreadData:
    url: str
    domain: str
    group: str
    thread_id: Optional[str]
    title: str
    topic_group: str
    fetched_at_utc: str
    messages: List[Message]


def read_links(path: Path) -> List[str]:
    seen = set()
    links = []
    for line in path.read_text(encoding="utf-8").splitlines():
        url = line.strip()
        if not url or url.startswith("#"):
            continue
        if url in seen:
            continue
        seen.add(url)
        links.append(url)
    return links


def request_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        },
    )
    with urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(value: str) -> str:
    value = unescape(value or "")
    value = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"</p\s*>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s*\n+", "\n", value)
    return value.strip()


def thread_id_from_url(url: str) -> Optional[str]:
    m = re.search(r"/(?:td-p|m-p)/(\d+)", url)
    return m.group(1) if m else None


def group_from_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [x for x in parsed.path.split("/") if x]
    board = "general"
    if "t5" in parts:
        try:
            board = parts[parts.index("t5") + 1]
        except (ValueError, IndexError):
            board = "general"
    return f"{parsed.netloc} / {board}"


def classify_topic(title: str) -> str:
    t = title.lower()
    if "pink line" in t or "pink-line" in t or "pink lines" in t:
        return "Pink Line Issue"
    if "green line" in t or "green-line" in t or "green lines" in t:
        return "Green Line Issue"
    if "brick" in t or "bricked" in t:
        return "Bricked After Update"
    if "update" in t:
        return "Update Related"
    return "Other"


def parse_message_node(node: ET.Element, source: str) -> Optional[Message]:
    body = node.findtext("body")
    text = strip_tags(body or "")
    if not text:
        return None

    author = node.findtext("./author/login")
    published = node.findtext("post_time")
    subject = node.findtext("subject")
    msg_id = node.findtext("id")

    return Message(
        id=msg_id,
        author=author,
        published=published,
        subject=subject,
        text=text,
        source=source,
    )


def fetch_root_message(domain: str, msg_id: str) -> Message:
    endpoint = f"https://{domain}/restapi/vc/messages/id/{msg_id}"
    xml_text = request_text(endpoint)
    root = ET.fromstring(xml_text)
    node = root.find("./message")
    if node is None:
        raise RuntimeError("Root message not found in API response.")
    parsed = parse_message_node(node, "root")
    if not parsed:
        raise RuntimeError("Root message had no extractable body.")
    return parsed


def resolve_root_thread_id(domain: str, msg_id: str) -> str:
    endpoint = f"https://{domain}/restapi/vc/messages/id/{msg_id}"
    xml_text = request_text(endpoint)
    root = ET.fromstring(xml_text)
    href = root.find("./message/root")
    if href is None:
        return msg_id
    raw = href.attrib.get("href", "")
    m = re.search(r"/messages/id/(\d+)", raw)
    return m.group(1) if m else msg_id


def fetch_comment_messages(domain: str, msg_id: str) -> List[Message]:
    page = 1
    page_size = 25
    ids: List[str] = []
    total_count: Optional[int] = None
    seen_ids = set()

    while True:
        endpoint = (
            f"https://{domain}/restapi/vc/messages/id/{msg_id}/comments"
            f"?page_size={page_size}&page={page}"
        )
        xml_text = request_text(endpoint)
        root = ET.fromstring(xml_text)

        if total_count is None:
            count_text = root.findtext("./comments/count")
            if count_text and count_text.isdigit():
                total_count = int(count_text)

        page_ids: List[str] = []
        for node in root.findall("./comments/messages/message"):
            cid = node.findtext("id")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                page_ids.append(cid)
                ids.append(cid)

        if not page_ids:
            break
        if total_count is not None and len(ids) >= total_count:
            break
        page += 1

    msgs: List[Message] = []
    for cid in ids:
        try:
            comment = fetch_root_message(domain, cid)
            comment.source = "comment"
            msgs.append(comment)
        except Exception:
            continue
    return msgs


def scrape_link(url: str) -> ThreadData:
    parsed = urlparse(url)
    link_msg_id = thread_id_from_url(url)
    if not link_msg_id:
        raise RuntimeError("Could not parse thread ID from URL.")

    root_id = resolve_root_thread_id(parsed.netloc, link_msg_id)
    root_msg = fetch_root_message(parsed.netloc, root_id)
    comments = fetch_comment_messages(parsed.netloc, root_id)

    # De-duplicate on message ID/text.
    seen = set()
    all_msgs: List[Message] = []
    for msg in [root_msg, *comments]:
        key = (msg.id, msg.text[:120])
        if key in seen:
            continue
        seen.add(key)
        all_msgs.append(msg)

    title = root_msg.subject or f"Thread {root_id}"
    return ThreadData(
        url=url,
        domain=parsed.netloc,
        group=group_from_url(url),
        thread_id=root_id,
        title=title,
        topic_group=classify_topic(title),
        fetched_at_utc=datetime.now(timezone.utc).isoformat(),
        messages=all_msgs,
    )


def main() -> None:
    links = read_links(LINKS_FILE)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    threads = []
    for i, url in enumerate(links, start=1):
        try:
            thread = scrape_link(url)
            threads.append(asdict(thread))
            print(f"[{i}/{len(links)}] OK  {url}")
        except Exception as exc:
            print(f"[{i}/{len(links)}] ERR {url} :: {exc}")
            threads.append(
                {
                    "url": url,
                    "domain": urlparse(url).netloc,
                    "group": group_from_url(url),
                    "thread_id": thread_id_from_url(url),
                    "title": "Failed to fetch",
                    "topic_group": "Fetch Error",
                    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                    "messages": [],
                    "error": str(exc),
                }
            )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_links": len(links),
        "threads": threads,
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {OUT_FILE} ({len(threads)} threads)")


if __name__ == "__main__":
    main()
