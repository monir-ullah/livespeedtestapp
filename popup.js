document.addEventListener("DOMContentLoaded", () => {
  const errorList = document.getElementById("error-list");

  // Fetch errors from background
  chrome.runtime.sendMessage({ type: "getErrors" }, (errors) => {
    if (errors.length === 0) {
      errorList.innerHTML = "<p>No errors captured.</p>";
      return;
    }

    errors.forEach((error, index) => {
      const errorBlock = document.createElement("div");
      errorBlock.className = "error-block";

      const title = document.createElement("h2");
      title.textContent = `Error ${index + 1}`;
      errorBlock.appendChild(title);

      const message = document.createElement("p");
      message.textContent = `Message: ${error.message}`;
      errorBlock.appendChild(message);

      const stack = document.createElement("pre");
      stack.textContent = `Stack Trace:\n${error.stack}`;
      errorBlock.appendChild(stack);

      errorList.appendChild(errorBlock);
    });
  });
});
