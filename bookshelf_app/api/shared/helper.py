from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), "JST")


class TimeUtil:
    @staticmethod
    def get_now() -> datetime:
        return datetime.now(JST)

    @staticmethod
    def get_jst(base: datetime) -> datetime:
        return base.astimezone(JST)
