// ==UserScript==
// @name         Salesforce Case Number Notifier
// @namespace    http://tampermonkey.net/
// @version      2.7
// @description  Sends the active Salesforce case number to a local server when it changes or when not viewing a case.
// @author       Anton Neledov - Palo Alto Networks
// @match        *://*.lightning.force.com/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // Identifier for logging
    const LOG_PREFIX = '[SCDO]';

    // State variables
    let lastCaseNumber = null;

    /**
     * Sends data to the local server using GM_xmlhttpRequest.
     * @param {string} caseNumber - The case number to send, or 'NO_CASE'.
     */
    function sendCaseNumber(caseNumber) {
        GM_xmlhttpRequest({
            method: 'POST',
            url: 'http://localhost:8000',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ case_number: caseNumber }),
            timeout: 5000, // 5 seconds timeout
            onload: function(response) {
                console.log(`${LOG_PREFIX} Sent case number: ${caseNumber}`);
            },
            onerror: function(error) {
                console.error(`${LOG_PREFIX} Error sending case number "${caseNumber}":`, error);
            },
            ontimeout: function() {
                console.error(`${LOG_PREFIX} Timeout while sending case number "${caseNumber}".`);
            }
        });
    }

    /**
     * Sends 'NO_CASE' to indicate no active Salesforce case is being viewed.
     */
    function sendNoCase() {
        if (lastCaseNumber === 'NO_CASE') {
            console.log(`${LOG_PREFIX} Already in 'NO_CASE' state. Skipping.`);
            return;
        }
        console.log(`${LOG_PREFIX} Sending 'NO_CASE' to server.`);
        lastCaseNumber = 'NO_CASE'; // Update the state before sending
        sendCaseNumber('NO_CASE');
    }

    /**
     * Extracts the active case number from the Salesforce page.
     * @returns {string|null} - The case number or null if not found.
     */
    function getActiveCaseNumber() {
        // Adjust the selector based on Salesforce's DOM structure
        const activeTab = document.querySelector('a[role="tab"][aria-selected="true"][title*="| Case"]');
        if (activeTab) {
            const titleAttr = activeTab.getAttribute('title');
            return titleAttr.split('|')[0].trim(); // Extract the case number before '|'
        }
        return null;
    }

    /**
     * Updates the current case number by checking the active Salesforce case.
     * Sends the case number if it has changed or 'NO_CASE' if no case is active.
     */
    function updateCaseNumber() {
        const currentCaseNumber = getActiveCaseNumber();

        console.log(`${LOG_PREFIX} Current Case Number: ${currentCaseNumber}`);
        console.log(`${LOG_PREFIX} Last Case Number: ${lastCaseNumber}`);

        if (currentCaseNumber) {
            if (currentCaseNumber !== lastCaseNumber) {
                console.log(`${LOG_PREFIX} Active Case Number changed to: ${currentCaseNumber}`);
                lastCaseNumber = currentCaseNumber;
                sendCaseNumber(currentCaseNumber);
            } else {
                console.log(`${LOG_PREFIX} Case number unchanged: ${currentCaseNumber}`);
            }
        } else {
            if (lastCaseNumber !== 'NO_CASE') {
                console.log(`${LOG_PREFIX} No active case detected. Sending 'NO_CASE'.`);
                sendNoCase();
            } else {
                console.log(`${LOG_PREFIX} Already in 'NO_CASE' state.`);
            }
        }
    }

    /**
     * Initializes event listeners for visibility changes and focus.
     */
    function initEventListeners() {
        // When the visibility of the page changes (e.g., tab switch)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log(`${LOG_PREFIX} Tab hidden. Sending 'NO_CASE'.`);
                sendNoCase();
            } else {
                console.log(`${LOG_PREFIX} Tab visible. Updating case number.`);
                // Delay to allow Salesforce's DOM to update upon becoming visible
                setTimeout(updateCaseNumber, 1000);
            }
        });

        // When the window gains focus
        window.addEventListener('focus', () => {
            console.log(`${LOG_PREFIX} Window gained focus. Updating case number.`);
            // Delay to allow Salesforce's DOM to update upon gaining focus
            setTimeout(updateCaseNumber, 1000);
        });

        // When the window loses focus
        window.addEventListener('blur', () => {
            console.log(`${LOG_PREFIX} Window lost focus. Sending 'NO_CASE'.`);
            sendNoCase();
        });

        // Before the window unloads (e.g., tab closure)
        window.addEventListener('beforeunload', () => {
            if (lastCaseNumber !== 'NO_CASE') {
                console.log(`${LOG_PREFIX} Before unload: Sending 'NO_CASE'.`);
                sendNoCase();
            }
        });

        console.log(`${LOG_PREFIX} Event listeners initialized.`);
    }

    /**
     * Initializes a MutationObserver to detect changes in the DOM.
     * This is useful for Single Page Applications like Salesforce.
     */
    function initMutationObserver() {
        const observer = new MutationObserver(() => {
            updateCaseNumber();
        });

        observer.observe(document.body, { childList: true, subtree: true });
        console.log(`${LOG_PREFIX} MutationObserver initialized.`);
    }

    /**
     * Initializes the script by setting up event listeners and MutationObserver.
     */
    function initializeScript() {
        initEventListeners();
        initMutationObserver();
        updateCaseNumber(); // Initial check
    }

    // Start the script
    initializeScript();

})();
