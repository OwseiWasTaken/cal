#! /usr/bin/python3.10
# imports
from util import *
from datetime import date, datetime

# TODO config file (lang, -d dates and stuff)

# TODO remove 2° arg and put it in sWEEKDAYS
#  i removed it and nothing wrong happend! how?!?!?!?
WEEKDAYS = [ # in pt-br
	"Segunda",
	"Terça",
	"Quarta",
	"Quinta",
	"Sexta",
	"Sábado",
	"Domingo",
]

sWEEKDAYS = list(map(lambda x:x[:3], WEEKDAYS))


class _month:
	def __init__(this, name, days):  # , SDotW): # Starting Day of the Week
		this.name = name
		this.days = days
		# this.SDotW = SDotW

	def __repr__(this):
		return f"{this.name} w/ {this.days} days"


MONTHS = [ # in pt-br
	_month("Dez", 31),
	_month("Jan", 31),
	_month("Fev", 28),
	_month("Mar", 31),
	_month("Abr", 30),
	_month("Mai", 31),
	_month("Jun", 30),
	_month("Jul", 31),
	_month("Ago", 31),
	_month("Set", 30),
	_month("Out", 31),
	_month("Nov", 30),
]


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


td = mktd()

# main
def Main() -> int:
	if not exists('Cal-config.xmp'):
		UseXmp('Cal-config.xmp', {})
	global td
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
	print(f"{td.dotws[0]}, {td.day} de {td.month.name} de {td.year}")
	PrintWeekDays()
	PrintMonth(prtmonth[0], prtmonth[1])
	# PrintMonth(*MakeMonth())
	return 0


checkdate = comreg(r"\d\d*,[012]?\d,[0123]?\d")


def IsDate(date: str) -> tuple[bool, tuple[str, str, str]]:
	s = checkdate.search(date)	# search
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
		print(f"{td.dotws[0]}, {td.day} de {td.month.name} de {td.year}")
		PrintWeekDays()
		PrintMonth(mnt[0], mnt[1])
		stdout.write(e)
		# ipt = input('e/d/q:').lower()
		ipt = read("e/d/q:").lower()
		if ipt == "q":
			ss("clear")
			stdout.write(s)
			print(f"{td.dotws[0]}, {td.day} de {td.month.name} de {td.year}")
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
		#TODO
		for _ in r(len(DtW)+datetime(td.year, td.monthi, 1).weekday()):
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
