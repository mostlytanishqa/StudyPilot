
from datetime import date, timedelta

from config import DIFFICULTY_WEIGHTS


def generate_schedule(topics, daily_hours):
    """
    Generate a study schedule using topic difficulty
    and examination deadlines.

    Easy   = 1.5 hours
    Medium = 3 hours
    Hard   = 4.5 hours
    """

    if daily_hours <= 0:
        raise ValueError("Daily study hours must be positive.")

    pending = [
        topic for topic in topics
        if not topic["completed"]
    ]

    if not pending:
        return []

    today = date.today()

    tasks = []

    # Calculate estimated workload for every topic.
    for topic in pending:

        difficulty = topic["difficulty"]

        weight = DIFFICULTY_WEIGHTS.get(difficulty)

        if weight is None:
            raise ValueError(
                f"Invalid difficulty: {difficulty}"
            )

        estimated_hours = weight * 1.5

        exam_date = topic.get("exam_date")

        if exam_date:
            deadline = date.fromisoformat(exam_date)
        else:
            deadline = today + timedelta(days=30)

        if deadline <= today:
            raise ValueError(
                f"Examination date for {topic['subject_name']} "
                "must be in the future."
            )

        tasks.append({
            "topic_id": topic["id"],
            "topic_name": topic["name"],
            "subject_name": topic["subject_name"],
            "deadline": deadline,
            "weight": weight,
            "remaining_hours": estimated_hours
        })

    # Prioritize earliest examinations.
    # For equal deadlines, prioritize harder topics.
    tasks.sort(
        key=lambda task: (
            task["deadline"],
            -task["weight"]
        )
    )

    schedule = []

    day_offset = 0
    daily_used = 0.0

    # Allocate available study hours.
    for task in tasks:

        remaining = task["remaining_hours"]

        while remaining > 0.0001:

            study_date = today + timedelta(
                days=day_offset
            )

            if study_date > task["deadline"]:
                raise ValueError(
                    f"Insufficient study time for "
                    f"{task['subject_name']}. "
                    "Increase your daily study hours "
                    "or adjust the examination date."
                )

            available = daily_hours - daily_used

            if available <= 0.0001:
                day_offset += 1
                daily_used = 0.0
                continue

            allocated = min(
                remaining,
                available
            )

            schedule.append({
                "topic_id": task["topic_id"],
                "topic_name": task["topic_name"],
                "subject_name": task["subject_name"],
                "date": study_date.isoformat(),
                "hours": round(allocated, 2)
            })

            remaining -= allocated
            daily_used += allocated

    return schedule
