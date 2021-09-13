var localDate = document.getElementById("localDate")
var localTime = document.getElementById("localTime")
var UTCDateTime = document.getElementById("UTCDateTime")

function setNow() {
	now = new Date()
	now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
	now.setSeconds(0)
	now.setMilliseconds(0)
	localDate.valueAsDate = now
	localTime.valueAsDate = now
}
document.getElementById("nowBtn").addEventListener("click", setNow)
setNow()

function updateUTC () {
	timestampParts = localDate.value.split('-').concat(localTime.value.split(':'))
	timestampParts[1]--
	timestampParts[5] = 0; // clear seconds
	UTCDateTime.value = new Date(...timestampParts).toISOString()
}
localDate.addEventListener("input", updateUTC)
localTime.addEventListener("input", updateUTC)
updateUTC()

var selects = document.getElementsByClassName("discreteSelect");
for (const el of selects) {
	el.addEventListener("input", function() {
		var d = (el.value == "_new" ? "" : "none");
		el.nextElementSibling.style.display = d;
	})
}
