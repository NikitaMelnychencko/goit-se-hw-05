class InvalidDaysError(Exception):
    pass


def parse_days(value) -> int:
    try:
        days = int(value)
    except (TypeError, ValueError):
        raise InvalidDaysError("Invalid argument command. Use only numbers.")
    if not 1 <= days <= 10:
        raise InvalidDaysError(
            f"Invalid command. Argument must be from 1 to 10. You entered {days}."
        )
    return days
