from typing import List, Dict, Any, Optional
from datetime import date, timedelta

class TimetableEngine:
    """
    Timetable Schedule & Projection Engine.
    Maps calendar dates against recurring weekly timetable slots to accurately
    calculate remaining classes in the semester.
    """

    @staticmethod
    def calculate_remaining_classes_by_subject(
        timetables: List[Any],
        from_date: date,
        semester_end_date: date
    ) -> Dict[str, int]:
        """
        Calculates remaining scheduled class periods per subject from (from_date + 1) to semester_end_date.
        """
        remaining_counts: Dict[str, int] = {}
        if from_date >= semester_end_date or not timetables:
            return remaining_counts

        # Pre-group timetable periods by day_of_week
        # day_of_week: 0=Mon, ..., 6=Sun
        day_schedule: Dict[int, List[Dict[str, Any]]] = {d: [] for d in range(7)}
        for entry in timetables:
            subj_id = entry.subject_id if hasattr(entry, "subject_id") else entry["subject_id"]
            dow = entry.day_of_week if hasattr(entry, "day_of_week") else entry["day_of_week"]
            periods = entry.periods_count if hasattr(entry, "periods_count") else entry.get("periods_count", 1)
            day_schedule[dow].append({"subject_id": str(subj_id), "periods": periods})
            if str(subj_id) not in remaining_counts:
                remaining_counts[str(subj_id)] = 0

        current_cursor = from_date + timedelta(days=1)
        while current_cursor <= semester_end_date:
            dow = current_cursor.weekday() # 0 is Monday in Python
            for item in day_schedule[dow]:
                remaining_counts[item["subject_id"]] += item["periods"]
            current_cursor += timedelta(days=1)

        return remaining_counts

    @staticmethod
    def get_classes_for_date(timetables: List[Any], target_date: date) -> List[Dict[str, Any]]:
        """
        Returns list of timetable entries scheduled for a specific date.
        """
        dow = target_date.weekday()
        matches = []
        for entry in timetables:
            e_dow = entry.day_of_week if hasattr(entry, "day_of_week") else entry["day_of_week"]
            if e_dow == dow:
                subj_id = entry.subject_id if hasattr(entry, "subject_id") else entry["subject_id"]
                start_time = entry.start_time if hasattr(entry, "start_time") else entry["start_time"]
                end_time = entry.end_time if hasattr(entry, "end_time") else entry["end_time"]
                room = entry.room if hasattr(entry, "room") else entry.get("room")
                periods = entry.periods_count if hasattr(entry, "periods_count") else entry.get("periods_count", 1)
                
                matches.append({
                    "subject_id": str(subj_id),
                    "day_of_week": dow,
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                    "room": room,
                    "periods_count": periods
                })
        return sorted(matches, key=lambda x: x["start_time"])
