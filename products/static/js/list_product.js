const slider = document.querySelector(".range-slider");
const progress = slider.querySelector(".progress");
const minPriceInput = slider.querySelector(".min-price");
const maxPriceInput = slider.querySelector(".max-price");
const minInput = slider.querySelector(".min-input");
const maxInput = slider.querySelector(".max-input");
const minLabel = slider.querySelector(".min-label");
const maxLabel = slider.querySelector(".max-label");

// Función para formatear número con puntos de miles
function formatPrice(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

const updateProgress = () => {
  const minValue = parseInt(minInput.value);
  const maxValue = parseInt(maxInput.value);

  const range = maxInput.max - minInput.min;
  const valueRange = maxValue - minValue;
  const width = (valueRange / range) * 100;
  const minOffset = ((minValue - minInput.min) / range) * 100;

  progress.style.width = width + "%";
  progress.style.left = minOffset + "%";

  minPriceInput.value = minValue;
  maxPriceInput.value = maxValue;

  // Actualizar etiquetas formateadas
  minLabel.textContent = "$" + formatPrice(minValue);
  maxLabel.textContent = "$" + formatPrice(maxValue);
};

const updateRange = (event) => {
  const input = event.target;

  let min = parseInt(minPriceInput.value);
  let max = parseInt(maxPriceInput.value);

  if (input === minPriceInput && min > max) {
    max = min;
    maxPriceInput.value = max;
  } else if (input === maxPriceInput && max < min) {
    min = max;
    minPriceInput.value = min;
  }

  minInput.value = min;
  maxInput.value = max;

  updateProgress();
};

minPriceInput.addEventListener("input", updateRange);
maxPriceInput.addEventListener("input", updateRange);

minInput.addEventListener("input", () => {
  if (parseInt(minInput.value) >= parseInt(maxInput.value)) {
    maxInput.value = minInput.value;
  }
  updateProgress();
});

maxInput.addEventListener("input", () => {
  if (parseInt(maxInput.value) <= parseInt(minInput.value)) {
    minInput.value = maxInput.value;
  }
  updateProgress();
});

progress.addEventListener("mousedown", (e) => {
  e.preventDefault();
  isDragging = true;
  startOffsetX = e.clientX - progress.getBoundingClientRect().left;
  slider.classList.toggle("dragging", isDragging);
});

updateProgress();
