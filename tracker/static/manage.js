stamps = document.getElementsByClassName("utc-timestamp");
for (const cell of stamps) {
	timestampParts = cell.innerText.split(/[-: ]/);
	timestampParts[1]--; // make months 0-indexed
	date = new Date(...timestampParts); // construct UTC date from strings
	date.setMinutes(date.getMinutes() - date.getTimezoneOffset()); // fix TZ
	dateParts = date.toString().split(' '); // pull apart for custom format
	dateParts[4] = dateParts[4].slice(0,5); // remove seconds
	cell.innerText = dateParts.slice(0,3).join(' ') + ", " + dateParts[4];
}

function setEditorVisibility(label, editor, visibility) {
	label.style.display  = visibility ? "none" : "";
	editor.style.display = visibility ? "" : "none";
}

labelDivs = document.getElementsByClassName("editor")
for (const labelDiv of labelDivs) {
	editBtn = labelDiv.firstElementChild;
	editDiv = labelDiv.nextElementSibling;
	cancelBtn = editDiv.firstElementChild;

	editDiv.style.display = "none";

	editBtn.addEventListener("click", setEditorVisibility.bind(null, labelDiv, editDiv, true));
	cancelBtn.addEventListener("click", setEditorVisibility.bind(null, labelDiv, editDiv, false));
}
