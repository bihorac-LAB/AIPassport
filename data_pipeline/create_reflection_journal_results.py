import os
import logging
import re

import pandas as pd
from collections import defaultdict
from typing import Literal

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionEntry, DiscussionTopic
from canvasapi.paginated_list import PaginatedList

logging.getLogger("canvasapi").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY", None)
CANVAS_URL = os.getenv("CANVAS_URL", None)
COURSE_ID = os.getenv("COURSE_ID", None)

def reflection_journal_col(module_num: str, col_type: Literal["post", "reply", "passed"]) -> str:
    if col_type == "post":
        return f"M{module_num}_RJ_Posted"
    elif col_type == "reply":
        return f"M{module_num}_RJ_Reply_Count"
    elif col_type == "passed":
        return f"M{module_num}_RJ_Passed"

def get_all_replies(entry: DiscussionEntry) -> list[DiscussionEntry]:
    """
    Replies may have replies, so we much check recursively
    """
    try:
        direct = list(entry.get_replies())
    except Exception:
        return []

    all_replies = []
    for r in direct:
        all_replies.append(r)
        all_replies.extend(get_all_replies(r))
    return all_replies

def create_reflection_journal_results(inmd_dir: str, logger: logging.Logger) -> tuple[str, str] | tuple[None, None]:
    """
    Fetches discussion post data from canvas api and creates a reflection_journal intermediate file.
    """
    if any(var is None for var in [API_KEY, CANVAS_URL, COURSE_ID]):
        logger.warning(f"Missing .env variables to fetch discussion posts")
        return None, None

    reflection_journal_fp = os.path.join(inmd_dir, "reflection_journal_results.csv")
    reflection_journal_keys_fp = os.path.join(inmd_dir, "reflection_journal_keys.csv")

    try:
        canvas = Canvas(CANVAS_URL, API_KEY)
        logger.info("Fetched canvas api successfully!")

        course: Course = canvas.get_course(COURSE_ID)
        logger.info(f"Obtained course {COURSE_ID} successfully!")

        topics: PaginatedList[DiscussionTopic] = course.get_discussion_topics()
        logger.info(f"Obtained discussion topics successfully!")
            
    except Exception as e:
        logger.error(f"Failed to fetch canvas api: {e}", exc_info=True)
        return None, None
    
    user_data = defaultdict(lambda: {
        "user_name": None,
        "modules": defaultdict(lambda: {
            "posted": 0,
            "replied_to": set()
        })
    })
    required_topic_attributes: list[str] = ["id", "title"]
    required_entry_attributes: list[str] = ["user_id", "user_name"]
    required_reply_attributes: list[str] = ["user_id", "user_name"]

    for topic in topics:
        if any(getattr(topic, attr, None) is None for attr in required_topic_attributes):
            logger.debug(f"Skipping invalid topic: {topic}")
            continue

        topic_title: str = topic.title.strip()
        module_match = re.search(r"Module\s+(\d+)", topic_title, re.IGNORECASE)
        if not module_match:
            continue
        module_num = int(module_match.group(1))

        # 2. check for reflection journal
        if "reflection journal" not in topic_title.lower():
            continue

        try:
            entries: PaginatedList[DiscussionEntry] = topic.get_topic_entries()
            logger.info(f"Successfully pulled topic entries for {topic_title}")

        except Exception as e:
            logger.error(f"Failed to get topic entries for module {module_num}: {e}", exc_info=True)
            continue

        for entry in entries:
            if any(getattr(entry, attr, None) is None for attr in required_entry_attributes):
                logger.debug(f"Skipping invalid entry: {entry}")
                continue

            uid = entry.user_id
            uname = entry.user_name

            user_data[uid]["user_name"] = uname
            user_data[uid]["modules"][module_num]["posted"] = 1

            try:
                replies: list[DiscussionEntry] = get_all_replies(entry=entry)
            except Exception as e:
                logger.debug(f"Failed to get replies for entry {entry.id}: {e}")
                replies = []

            for reply in replies:
                if any(getattr(reply, attr, None) is None for attr in required_reply_attributes):
                    logger.debug(f"Skipping invalid reply: {reply}")
                    continue

                reply_uid = reply.user_id
                reply_uname = reply.user_name

                user_data[reply_uid]["user_name"] = reply_uname

                # do not count self-replies
                if reply_uid != uid:
                    user_data[reply_uid]["modules"][module_num]["replied_to"].add(uid)

    # collect all module numbers
    all_modules: list[int] = sorted({
        module_num
        for udata in user_data.values()
        for module_num in udata["modules"].keys()
    })

    rows: list[dict] = []
    for uid, udata in user_data.items():
        row: dict = {
            "user_id": uid,
            "user_name": udata["user_name"]
        }

        for module_num in all_modules:
            posted_col = reflection_journal_col(module_num=module_num, col_type="post")
            reply_count_col = reflection_journal_col(module_num=module_num, col_type="reply")
            passed_col = reflection_journal_col(module_num=module_num, col_type="passed")

            row[posted_col] = udata["modules"][module_num]["posted"]
            row[reply_count_col] = len(udata["modules"][module_num]["replied_to"])
            row[passed_col] = 1 if (row[posted_col] and row[reply_count_col] >= 2) else 0
            
        rows.append(row)

    df: pd.DataFrame = pd.DataFrame(rows).fillna(0)

    # Metadata table describing the columns
    reflection_journal_key_rows: list[dict] = []
    for module_num in all_modules:
        reflection_journal_key_rows.append({
            "Variable" : reflection_journal_col(module_num=module_num, col_type="post"),
            "Module" : f"Whether the student created a discussion post for module {module_num} reflection journal",
            "Module Number" : module_num,
        })
        reflection_journal_key_rows.append({
            "Variable" : reflection_journal_col(module_num=module_num, col_type="reply"),
            "Module" : f"The number of replies to other student's discussion posts for module {module_num} reflection journal",
            "Module Number" : module_num,
        })
        reflection_journal_key_rows.append({
            "Variable" : reflection_journal_col(module_num=module_num, col_type="passed")
,
            "Module" : f"Whether the student passed the reflection journal participation requirements for module {module_num} reflection journal",
            "Module Number" : module_num,
        })
    reflection_journal_keys = pd.DataFrame(reflection_journal_key_rows)
    reflection_journal_keys.to_csv(reflection_journal_keys_fp, index=False)

    df.to_csv(reflection_journal_fp, index=False)
    logger.info(f"Wrote reflection journal results to {reflection_journal_fp}")

    return reflection_journal_fp, reflection_journal_keys_fp
