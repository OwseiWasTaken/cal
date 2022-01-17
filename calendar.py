#! /usr/bin/python3.10
# imports
from util import *
from datetime import date, datetime

# TODO config file (lang, -d dates and stuff)


WEEKDAYS = []
sWEEKDAYS = []
MONTHS = []


@dataclass
class _month:
    name: str
    days: int

    def __repr__(this):
        return f"{this.name} w/ {this.days} days"


def ReadXmp():
    global MONTHS, WEEKDAYS, sWEEKDAYS
    if not exists("Cal-config.xmp"):
        UseXmp("Cal-config.xmp", InitConfig())
    xmp = UseXmp("Cal-config.xmp")
    if not "use-lang" in xmp.keys():
        xmp["use-lang"] = "en-us"
        UseXmp("Cal-config.xmp", xmp)
    uselang = xmp["use-lang"]
    sm = xmp["lang"][uselang]["months"]
    sw = xmp["lang"][uselang]["weekdays"]
    MONTHS = [  # in pt-br
        _month(sm[11], 31),  # TODO # remove this month, monthi-1, mend bronken
        _month(sm[0], 31),
        _month(sm[1], 28),
        _month(sm[2], 31),
        _month(sm[3], 30),
        _month(sm[4], 31),
        _month(sm[5], 30),
        _month(sm[6], 31),
        _month(sm[7], 31),
        _month(sm[8], 30),
        _month(sm[9], 31),
        _month(sm[10], 30),
        _month(sm[11], 31),
    ]
    WEEKDAYS = [  # in pt-br
        sw[0],
        sw[1],
        sw[2],
        sw[3],
        sw[4],
        sw[5],
        sw[6],
    ]
    sWEEKDAYS = list(map(lambda x: x[:3], WEEKDAYS))


@dataclass
class Td:
    date: int
    day: int
    month: _month
    monthi: int
    dotw: int
    dotws: str
    year: int


def mktd(date=date.today()):
    today = date
    year = today.year
    monthi = today.month
    month = MONTHS[monthi]
    dotw = today.weekday()
    return Td(
        today,
        today.day,
        month,
        monthi,
        dotw,
        WEEKDAYS[dotw],
        year,
    )


td = None

# main
def Main() -> int:
    if not exists("Cal-config.xmp"):
        UseXmp("Cal-config.xmp", InitConfig())
    ReadXmp()  # set global WEEKDAYS and MONTHS
    global td
    td = mktd()
    assert td
    prtmonth = MakeMonth()
    if get("-i").exists:  # interactive
        Interective(prtmonth)
        return 0
    # TODO
    # -d date = search config file for
    # date's name
    # mktd(...), MakeMonth()
    # OR
    # then add to reader ['d', 'yyyy,mm,dd', 'q']
    print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
    PrintWeekDays()
    PrintMonth(prtmonth[0], prtmonth[1])
    # PrintMonth(*MakeMonth())
    return 0


checkdate = comreg(r"\d\d*,[012]?\d,[0123]?\d")


def IsDate(date: str) -> tuple[bool, tuple[str, str, str]]:
    s = checkdate.search(date)  # search
    if s == None:
        return (False, (-1, -1, -1))
    ss = s.string  # search string
    stf = list(map(lambda x: int(x), ss.split(",")))
    if len(stf) == 3:
        year, month, day = stf
    else:
        year = -1  # possible, bruh
        month = -1
        day = -1
    return (s != None and 13 > month > 0 and 32 > day > 0), (year, month, day)


reader: list[str] = []
if get("-r").exists:
    reader = get("-r").list
pirc = get("--print-input-even-with-reader-cli", "--pirc")


def read(prt: str) -> str:
    if len(reader):
        if pirc:
            sout.write(ipt)
        return reader.pop(0)
    else:
        return input(prt)


def Interective(prtmonth):
    global td
    # print(IsDate('3,4,3'))
    # print(IsDate('3,0,0003'))
    x, y = GetTerminalSize()
    mnt = MakeMonth()
    strictdate = get("--strict", "-s").exists
    s = pos(0, 0)
    e = pos(y - 2, 0)
    ee = pos(y - 1, 0)
    while True:
        ss("clear")
        stdout.write(s)
        print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
        PrintWeekDays()
        PrintMonth(mnt[0], mnt[1])
        stdout.write(e)
        # ipt = input('e/d/q:').lower()
        ipt = read("e/d/q:").lower()
        if ipt == "q":
            ss("clear")
            stdout.write(s)
            print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
            PrintWeekDays()
            PrintMonth(mnt[0], mnt[1])
            return
        elif ipt == "r":
            import calendar

            return calendar.Main()
        elif ipt == "e":  # edit day
            assert 0, "udev"
        elif ipt == "cq":
            ss("clear")
            stdout.write(s)
            return
        elif ipt == "d":
            ClearLine(y - 2)
            stdout.write(e)
            # idt, dt = IsDate(input("date:"))
            idt, dt = IsDate(read("date:"))
            if not strictdate:
                idt = idt | (dt != (-1, -1, -1))
            # idt = idt|( (not strictdate) and dt != (-1, -1, -1) )
            if idt:
                td = mktd(datetime(dt[0], dt[1], dt[2]))
                mnt = MakeMonth()
            else:
                stdout.write(ee + color.Red + "[can't read date!]" + color.Reset)
        else:
            stdout.write(ee + color.Red + f"[no such command `{ipt}`]" + color.Reset)


def PrintWeekDays():
    print(" ".join(sWEEKDAYS))


def MakeMonth() -> tuple[list[int], int, tuple[int, int]]:
    DtW = []
    borders = (0, 0)
    if datetime(td.year, td.monthi, 1).weekday() != 0:
        i = MONTHS[td.monthi - 1].days
        # TODO
        for _ in r(len(DtW) + datetime(td.year, td.monthi, 1).weekday()):
            borders = borders[0] + 1, borders[1]
            DtW.append(i)
            i -= 1
        DtW = DtW[::-1]
        DtW += [x + 1 for x in r(td.month.days)]

        i = 0
        while len(DtW) % 7:
            borders = borders[0], borders[1] + 1
            DtW.append((i := i + 1))
    else:
        DtW += [x + 1 for x in r(td.month.days)]
        i = 0
        while len(DtW) % 7:
            DtW.append((i := i + 1))
            borders = borders[0], borders[1] + 1
    for i in r(DtW):
        if DtW[i] == td.day:
            break
    return DtW, i, borders


def PrintMonth(dtw: list[str], select):
    grey = True
    w = -1
    sout.write("\x1b[2;37m")
    for i in r(dtw):
        if dtw[i] == 1:
            grey = not grey
            if grey:
                sout.write("\x1b[2;37m")
            else:
                sout.write("\x1b[0m")
        w += 1
        if not w % 7:
            w = 0
            print()
        if i == select:
            print(
                "\x1b[7;37m" + str(dtw[i]), end="\x1b[0m" + " " * (4 - len(str(dtw[i])))
            )
            if grey:
                sout.write("\x1b[2;37m")
            else:
                sout.write("\x1b[0m")
        else:
            print(dtw[i], end=" " * (4 - len(str(dtw[i]))))
    sout.write("\x1b[0m\n")


def InitConfig() -> dict[Any]:  # fu, not type hinting this shit
    return {
        "use-lang": "en-us",
        "lang": {
            "pt-br": {
                "weekdays": {
                    (
                        "Segunda",
                        "Terça",
                        "Quarta",
                        "Quinta",
                        "Sexta",
                        "Sábado",
                        "Domingo",
                    )
                },
                "months": {
                    (
                        "Jan",
                        "Fev",
                        "Mar",
                        "Abr",
                        "Mai",
                        "Jun",
                        "Jul",
                        "Ago",
                        "Set",
                        "Out",
                        "Nov",
                        "Dez",
                    )
                },
            },
            "en-us": {
                "weekdays": {
                    (
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    )
                },
                "months": {
                    (
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Agu",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    )
                },
            },
        },
        "dates": {
            # none by default
        },
    }


# start
if __name__ == "__main__":
    start = tm()
    ExitCode = Main()

    if get("--debug").exists:
        if not ExitCode:
            printl("%scode successfully exited in " % COLOR.green)
        else:
            printl("%scode exited with error %d in " % (COLOR.red, ExitCode))
        print("%.3f seconds%s" % (tm() - start, COLOR.nc))
    exit(ExitCode)
