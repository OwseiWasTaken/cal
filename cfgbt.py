from typing import Callable, Any, Optional, Iterator, Iterable

def OnXmp(xmp:dict[str, Any], path:Iterable[str], AlwaysReturnFoud=False) -> tuple[int, Any]: # (error index (0 = OK) , value)
	rn = xmp
	path = path.copy() # de-ref array
	noret = None
	r = 0
	if len(path) > 0:
		next = path.pop(0)
		if next in rn.keys():
			rn = xmp[next]
		else:
			if AlwaysReturnFoud:
				return r, rn
			return r, noret
	while len(path):
		r += 1
		next = path.pop(0)
		if next in rn.keys():
			rn = rn[next]
		else:
			if AlwaysReturnFoud:
				return r, rn
			return r, noret
		if len(path) == 0:
			return 0, rn
	else:
		return 0, rn

def InitConfig() -> dict[str, Any]:
	return {
		"use-lang": "en-us",
		"lang": {
			"pt-br": {
				"weekdays": (
					"Segunda",
					"Terça",
					"Quarta",
					"Quinta",
					"Sexta",
					"Sábado",
					"Domingo",
				),
				"months": (
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
				),
			},
			"en-us": {
				"weekdays": (
					"Monday",
					"Tuesday",
					"Wednesday",
					"Thursday",
					"Friday",
					"Saturday",
					"Sunday",
				),
				"months": (
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
				),
			},
		},
		"dates": {
			# none by default
		},
		"people": {
			# none by default
		}
	}

