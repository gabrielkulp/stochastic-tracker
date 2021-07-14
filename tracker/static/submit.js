function selectUpdate(t) {
	// show the new tag text box if "new" is selected
	var newTagDiv = t.parentElement.nextSibling;
	newTagDiv.style.display = (t.value.includes("new") ? "block" : "none");
	newTagDiv.children[0].required = (t.value.includes("new"));

	// include current or previous tag index in form
	if (t.previousElementSibling) {
		if (t.value == "done") {
			t.name = "";
			t.previousElementSibling.name = "glimpses[]";
		} else {
			t.name = "glimpses[]";
			t.previousElementSibling.name = "";
		}
	}

	// make sure any subsequent selectors are still needed
	if (t.nextElementSibling) {
		if (t.nextElementSibling.children.length == 2 ||
				tags[t.nextElementSibling.children[1].value].parent != t.value)
			while (t.nextElementSibling)
				t.nextElementSibling.remove();
	}

	// check if current selection needs children added
	if (tags[t.value] && !t.nextElementSibling) {
		var newSelect = document.createElement("select");
		t.parentElement.appendChild(newSelect);

		newSelect.name = "glimpses[]";
		newSelect.addEventListener("click", ()=>selectUpdate(newSelect));

		// add all the options
		var newOption = document.createElement("option");
		newOption.value = "done";
		newOption.innerText = "⮨ done"; //⟵⟸⬅⮨⮜←
		newSelect.appendChild(newOption);

		for (i in tags[t.value].children) {
			newOption = document.createElement("option");
			newOption.value = tags[tags[t.value].children[i]].idx;
			newOption.innerText = tags[tags[t.value].children[i]].name;
			newSelect.appendChild(newOption);
		}

		newOption = document.createElement("option");
		newOption.value = "new" + t.value;
		newOption.innerText = "🖉 new"; //+✚⮯⮟✎🖉🖊🖋⌨
		newSelect.appendChild(newOption);
		selectUpdate(newSelect);
	}
}

function tagAdd(defaultIdx) {
	var gl = document.getElementById("glimpseList");

	var newItem = document.createElement("li");
	gl.appendChild(newItem);

	var newButton = document.createElement("button");
	newItem.appendChild(newButton);

	newButton.addEventListener("click", ()=>newItem.remove());
	newButton.innerText = "✖"; //X❌✖🗑

	var div1 = document.createElement("div");
	div1.style.display = "inline";
	newItem.appendChild(div1);

	var newSelect = document.createElement("select");
	div1.appendChild(newSelect);
	newSelect.addEventListener("click", ()=>selectUpdate(newSelect));

	// don't add a "none" option for top-level
	for (i in tags) {
		if (!tags[i].parent) {
			var newOption = document.createElement("option");
			newOption.value = tags[i].idx;
			newOption.innerText = tags[i].name;
			newSelect.appendChild(newOption);
		}
	}

	// (don't) add a "new" option for top-level tags
/*	var newOption = document.createElement("option");
	newOption.value = "new";
	newOption.innerText = "-- new --";
	newSelect.appendChild(newOption);
*/
	newSelect.name = "glimpses[]";
	newSelect.autocomplete = "off";
	newSelect.selectedIndex = defaultIdx;
	newSelect.required = true;

	var div2 = document.createElement("div");
	div2.style.display = "none";
	div2.appendChild(document.createElement("input"));
	div2.children[0].type = "text";
	div2.children[0].name = "newTags[]";

	newItem.appendChild(div2);

	// trigger adding child selection if needed
	if (defaultIdx != -1)
		selectUpdate(newSelect);
}
document.getElementById("tagAdd").addEventListener("click", ()=>tagAdd(-1));

function nowToggle(t) {
	var d = (t.checked ? "none" : "block");
	t.nextElementSibling.style.display = d;
}

var check = document.getElementById("nowCheckbox");
check.addEventListener("click", ()=>nowToggle(check));
nowToggle(check); // make sure it's up to date

// pre-load one of each top-level tag
for (i in tags)
	if (!tags[i].parent)
		tagAdd(i);
