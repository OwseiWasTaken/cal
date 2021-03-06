#! /usr/bin/python3.10
# imports
from util import *
from datetime import date, datetime
from cfgbt import InitConfig, OnXmp

WEEKDAYS = []
sWEEKDAYS = []
MONTHS = []
# set config file (same folder as calendar.py)
confile = "/".join(__file__.split("/")[:-1]) + "/Config.xmp"


@dataclass
class _month:
	name: str
	days: int

	def __repr__(this):
		return f"{this.name} w/ {this.days} days"

# get xmp content, set it to global vars and returns the tree
def ReadXmp():
	global MONTHS, WEEKDAYS, sWEEKDAYS
	if not exists(confile):
		UseXmp(confile, InitConfig())
	xmp = UseXmp(confile)
	if not "use-lang" in xmp.keys():
		xmp["use-lang"] = "en-us"
		UseXmp(confile, xmp)
	uselang = xmp["use-lang"]
	sm = xmp["lang"][uselang]["months"]
	sw = xmp["lang"][uselang]["weekdays"]
	MONTHS = [	# in pt-br
		# _month(sm[11], 31),
		_month(sm[0], 31),
		_month(sm[1], 28),	# feb
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
	return xmp


@dataclass
class Td:
	date: int
	day: int
	month: _month
	monthi: int
	pmonth: int
	dotw: int
	dotws: str
	year: int

# makes ToDay DataClass
def mktd(date=date):
	today = date
	year = today.year
	monthi = today.month
	month = MONTHS[monthi - 1]
	dotw = today.weekday()
	if monthi == 0:
		pmonth = 11
	else:
		pmonth = monthi - 2
	if monthi == 2:
		# add leap year's day depending on year
		month.days += IsLeapYear(year)
	return Td(
		today,
		today.day,
		month,
		monthi,
		pmonth,
		dotw,
		WEEKDAYS[dotw],
		year,
	)

td = None
date = date.today()
# make conf global
conf:dict[str, Any] = {}

# main
def Main() -> int:
	if get("-h", "--help").exists:
		return help(get("-h", "--help").list)
	if not exists(confile):
		UseXmp(confile, InitConfig())
	global td, conf
	conf = ReadXmp()  # set global WEEKDAYS and MONTHS
	td = mktd(date)
	prtmonth = MakeMonth()

	# startup date set
	if get("-d").exists:
		if len(get("-d").list) == 1:
			d = get("-d").first
			r, v = OnXmp(conf, ['dates', d, 'date'])
			if not r:
				r, dt = IsDate(v)
				if not r:
					td = mktd(datetime(*dt))
					prtmonth = MakeMonth()
			else:
				r, dt = IsDate(d)
				if r:
					td = mktd(datetime(*dt))
					prtmonth = MakeMonth()
				else:
					stderr.write(f"can't read date from -d {d}\n")
					return 3
		else: # -d with no extra args
			fprintf(
				stderr,
				"-d option uses 1 and only 1 argument!, not {d}\n",
				len(get("-d").list),
			)
			return 1

	if get("-i").exists:  # interactive mode
		return Interactive()
	print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
	PrintWeekDays()
	PrintMonth(prtmonth[0], prtmonth[1])
	# PrintMonth(*MakeMonth())
	return 0


# regex to check if date can be parsed
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
	return (s != None and 13 > month > 0 and 32 > day > 0 and year > 0), (
		year,
		month,
		day,
	)


reader: list[str] = []
if get("-r").exists:
	reader = get("-r").list
erc = get("--echo-reader-cli", "--pirc", "--erc") # pirc is the old name


def read(st: str) -> str:
	if len(reader):
		ipt = reader.pop(0)
		if erc:
			print(ipt)
		return ipt
	else:
		return input(st)


#info format
def InFormat(v:Any) -> str:
	extra = str(v)
	if type(v) in (tuple, list, set):
		extra = f"{', '.join([InFormat(x) for x in v])}"
	if isinstance(v, str):
		extra = f"\"{v}\""
	return extra

def Interactive():
	global td, conf
	_, y = GetTerminalSize()
	prtmonth = MakeMonth()
	s = pos(0, 0)
	e = pos(y - 2, 0)
	ee = pos(y - 1, 0)
	extra = ''
	pdt = {}
	while True:
		ss("clear")
		stdout.write(s)
		print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
		PrintWeekDays()
		PrintMonth(prtmonth[0], prtmonth[1])

		stdout.write(extra)
		extra = ""

		stdout.write(e)
		ipt = read("$").lower()
		if ipt == 'q': # quit
			ss("clear")
			stdout.write(s)
			print(f"{td.dotws}, {td.day} de {td.month.name} de {td.year}")
			PrintWeekDays()
			PrintMonth(prtmonth[0], prtmonth[1])
			return 0

		elif ipt == 'r': # reload
			from calendar import Main, WEEKDAYS, sWEEKDAYS, MONTHS, confile, td, date, conf

			return Main()

		elif ipt in ('i',"info"):
			# to format
			for k, v in pdt.items():
				if k == "date":
					continue
				k = f"\n{k}: "
				if k == "desc":
					k=''
				extra += k+InFormat(v)
				pass

		elif ipt in ('l', "list", 'h', "help"): # help
			stdout.write(ee)
			stdout.write("\x1b[2;37m")
			stdout.write(
				"q:quit, r:reload, l:list, e:edit date, cq:clear quit, d:goto date (name or yyyy,mm,dd), ld: list xmp dates"
			)
			stdout.write("\x1b[0m")

		elif ipt == 'e':  # edit date
			nm = read('name:')
			conf['dates'][nm] = {'date':f'{td.year},{td.monthi},{td.day}'}
			dt = conf['dates'][nm]
			UseXmp(confile, conf)

		elif ipt == 'ld': # list dates
			extra = '\n'.join(['>'+i+' @ '+conf['dates'][i]['date'].replace(',', '-') for i in conf['dates']])

		elif ipt == "cq": # clear;quit
			ss("clear")
			stdout.write(s)
			return 0

		elif ipt == 'd': # goto date
			ClearLine(y - 2)
			stdout.write(e)
			rd = read('date:')
			idt, dt = IsDate(rd)

			r, v = OnXmp(conf, ['dates', rd, 'date'], 1)
			if r:
				if not strictdate:
					idt = dt != (-1, -1, -1)
				if idt and len(dt) == 3:
					td = mktd(datetime(*dt))
					mnt = MakeMonth()
				else:
					stdout.write(ee + color.Red + "[can't read date!]" + color.Reset)
			else:
				#r, v = OnXmp(conf, ['dates', rd, 'date'], 1)
				# date name
				r, dt = IsDate(v)
				if not r:
					stdout.write(ee + color.Red + f"[can't convert `{v}` to date]" + color.Reset)
				else:
					td = mktd(datetime(*dt))
					mnt = MakeMonth()

		else:
			stdout.write(ee + color.Red + f"[no such command `{ipt}`] type `help` or `list` to list commands" + color.Reset)


def PrintWeekDays():
	print(" ".join(sWEEKDAYS))


def MakeMonth() -> tuple[list[int], int, tuple[int, int]]:
	DtW = []
	borders = (0, 0)
	if datetime(td.year, td.monthi, 1).weekday() != 0:
		i = MONTHS[td.pmonth].days
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
	# don't get past month's (on next's) day
	om = False
	for i in r(DtW):
		if DtW[i] == 1:
			om = not om
		if DtW[i] == td.day and om:
			break
	return DtW, i, borders

# format and print month string (list[str])
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


def help(show: list[str]):
	printf(
		"usage: {s} [-d Date ] [-i interactive [-r read]] [-h [i/d/h]]\n",
		argv[0],
	)
	expl = {
		"d": """
-d goto date by name: instead of starting the calendar with the current date,
start at the date in Config.xmp
e.g
Config.xmp:
<dates>
	<birtday>
		[date 'YYYY,MM,DD']
		[desc 'my birtday!!!']
	</birtday>

	<DATE_NAME>
		[desc 'some date']
		[date 'YYYY,MM,DD']
	</DATE_NAME>
</dates>
$%s -d birtday
instead of starting the calendar at %s,
it will start at YYYY,MM,DD defined by the config file
"""
		% (argv[0], date.today()),
		"i": """
-i interactive mode:
instead of just printing the calendar, you can
q:quit, r:reload calendar, l:list, e:edit date, cq:clear quit, d:goto date
e.g
$./calendar.py -i
<calendar printed>
$$d
date:2000,3,3 (this will change the calendar's date to 2000-3-3)
$$r
(this will reload the program)
$$l
"q:quit, r:reload calendar, l:list, e:edit date, cq:clear quit, d:goto date"
$$cq
clear and quit

[-r reader]
instead of using input, the program will get arguments passed to -r as input
e.g
$$./calendar.py -i -r d 2000,3,3
this ill work the same as calendar.py, then typing d, then 2000,3,3
""",
		"h": """
-h [i/d/h]
will display this
""",
	}
	for i in show:
		if i in expl.keys():
			print(expl[i])
		else:
			fprintf(
				stderr,
				"can't print specific help of `{s}`, it does not exist\n-h [i/d/h]\n",
				i,
			)
			return 5
	return 0


