// Listen for error messages
document.addEventListener("error", (event) => {
  const errorMessage =
    event.error?.message || event.message || "No error message";
  const errorStack = event.error?.stack || "No stack trace available";

  chrome.runtime.sendMessage({
    type: "error",
    message: errorMessage,
    stack: errorStack,
  });
});
