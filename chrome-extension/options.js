// Saves options to chrome.storage
const saveOptions = () => {
    const apiUrlValue = document.getElementById('apiUrl').value;
  
    chrome.storage.sync.set(
      { apiUrl: apiUrlValue },
      () => {
        // Update status to let user know options were saved.
        const status = document.getElementById('status');
        status.textContent = 'Options saved.';
        setTimeout(() => {
          status.textContent = '';
        }, 750);
      }
    );
  };
  
  // Restores select box and checkbox state using the preferences
  // stored in chrome.storage.
  const restoreOptions = () => {
    chrome.storage.sync.get(
      { apiUrl: 'http://localhost:8000/download'},
      (items) => {
        document.getElementById('apiUrl').value = items.apiUrl;
      }
    );
  };
  
  document.addEventListener('DOMContentLoaded', restoreOptions);
  document.getElementById('save').addEventListener('click', saveOptions);