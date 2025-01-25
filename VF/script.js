document.querySelector("body > div > main > div:nth-child(2) > div:nth-child(3) > md-list-item").shadowRoot.querySelector("#item > md-item").style.overflow = "visible";
let svgElement;

async function loadSVG(hexValue) {
	try {
		const response = await fetch(`https://seeki.vistudium.top/SVG/${hexValue}.svg`);
		if (!response.ok) {
			throw new Error('SVG加载失败');
		}
		const svgText = await response.text();
		const svgContainer = document.getElementById("svgContainer");
		svgContainer.innerHTML = svgText;
		svgElement = svgContainer.querySelector("svg");
		svgElement.style.strokeLinejoin = "miter";
		svgElement.style.strokeWidth = "0";
	} catch (error) {
		alert(error.message);
	}
}

document.getElementById("loadSVGButton").addEventListener("click", () => {
	const hexValue = document.getElementById("hexInput").value;
	loadSVG(hexValue);
});

let currentLinejoin = "miter";
document.getElementById("changeStyleButton").addEventListener("click", () => {
	const linejoinStyles = ["bevel", "miter", "round"];
	const currentIndex = linejoinStyles.indexOf(currentLinejoin);
	currentLinejoin = linejoinStyles[(currentIndex + 1) % linejoinStyles.length];
	svgElement.style.strokeLinejoin = currentLinejoin;
});

document.getElementById("strokeWidthSlider").addEventListener("input", (event) => {
	const sliderValue = parseInt(event.target.value);
	let strokeWidth;

	if (sliderValue === 100) {
		strokeWidth = document.getElementById("strokeWidth100").value;
	} else if (sliderValue === 1000) {
		strokeWidth = document.getElementById("strokeWidth1000").value;
	} else if (sliderValue < 400) {
		const normalizedValue = (sliderValue - 100) / (400 - 100);
		strokeWidth = `${parseFloat(document.getElementById("strokeWidth100").value) * (1 - normalizedValue)}rem`;
	} else {
		const normalizedValue = (sliderValue - 400) / (1000 - 400);
		strokeWidth = `${parseFloat(document.getElementById("strokeWidth1000").value) * normalizedValue}rem`;
	}

	svgElement.style.strokeWidth = strokeWidth;

	if (sliderValue > 400) {
		svgElement.style.stroke = document.getElementById("strokeColorHigh").value;
	} else {
		svgElement.style.stroke = document.getElementById("strokeColorLow").value;
	}
});

loadSVG("323b9");