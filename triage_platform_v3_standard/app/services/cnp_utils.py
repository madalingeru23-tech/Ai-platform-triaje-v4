from datetime import date

def parse_cnp(cnp: str):
    if len(cnp) != 13 or not cnp.isdigit():
        raise ValueError("CNP invalid")

    s = int(cnp[0])
    yy = int(cnp[1:3])
    mm = int(cnp[3:5])
    dd = int(cnp[5:7])

    if s in (1, 2):
        year = 1900 + yy
    elif s in (5, 6):
        year = 2000 + yy
    elif s in (3, 4):
        year = 1800 + yy
    else:
        year = 1900 + yy

    birth_date = date(year, mm, dd)
    sex = "M" if s % 2 == 1 else "F"
    return birth_date, sex

def calculate_age(birth_date: date, today: date | None = None) -> int:
    if today is None:
        today = date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years
