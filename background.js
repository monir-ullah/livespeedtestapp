let errorLogs = [];

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "error") {
    errorLogs.push(message);
  }
});

// Provide errors to the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "getErrors") {
    sendResponse(errorLogs);
  }
});
