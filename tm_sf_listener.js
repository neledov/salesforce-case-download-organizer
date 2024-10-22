// ==UserScript==
// @name         Salesforce Case Number Notifier
// @namespace    http://tampermonkey.net/
// @version      3.1
// @description  Sends the active Salesforce case number and company name to a local server when they change or when not viewing a case.
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
    let lastCompanyName = null;

    /**
     * Sends data to the local server using GM_xmlhttpRequest.
     * @param {string} caseNumber - The case number to send, or 'NO_CASE'.
     * @param {string|null} companyName - The company name associated with the case, or 'NO_COMPANY'.
     */
    function sendNotification(caseNumber, companyName) {
        GM_xmlhttpRequest({
            method: 'POST',
            url: 'http://localhost:8000',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                case_number: caseNumber,
                company_name: companyName
            }),
            timeout: 5000, // 5 seconds timeout
            onload: function(response) {
                console.log(`${LOG_PREFIX} Sent case number: ${caseNumber}, Company Name: ${companyName}`);
            },
            onerror: function(error) {
                console.error(`${LOG_PREFIX} Error sending data:`, error);
            },
            ontimeout: function() {
                console.error(`${LOG_PREFIX} Timeout while sending data.`);
            }
        });
    }

    /**
     * Sends 'NO_CASE' and 'NO_COMPANY' to indicate no active Salesforce case is being viewed.
     */
    function sendNoCaseAndCompany() {
        if (lastCaseNumber === 'NO_CASE' && lastCompanyName === 'NO_COMPANY') {
            console.log(`${LOG_PREFIX} Already in 'NO_CASE' and 'NO_COMPANY' state. Skipping.`);
            return;
        }
        console.log(`${LOG_PREFIX} Sending 'NO_CASE' and 'NO_COMPANY' to server.`);
        lastCaseNumber = 'NO_CASE'; // Update the state before sending
        lastCompanyName = 'NO_COMPANY';
        sendNotification('NO_CASE', 'NO_COMPANY');
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
     * Extracts the company name from a specific section of the Salesforce page using regex.
     * @returns {string|null} - The company name or null if not found.
     */
    function getCompanyName() {
        // Selector targeting the specific container where the company name resides
        const containerSelector = 'div.windowViewMode-maximized.active.lafPageHost';
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn(`${LOG_PREFIX} Company container not found using selector: "${containerSelector}"`);
            return null;
        }

        const regex = /href="\/lightning\/r\/Account\/[^"]+"[^>]*?>.*?<slot[^>]*?>.*?<slot[^>]*?>([^<]+)<\/slot>/;
        const htmlContent = container.innerHTML;
        const match = htmlContent.match(regex);
        if (match) {
            return match[1].trim();
        } else {
            console.warn(`${LOG_PREFIX} Company name not found using the provided regex.`);
            return null;
        }
    }

    /**
     * Updates the current case number and company name by checking the active Salesforce case.
     * Sends the case number and company name if they have changed or 'NO_CASE' and 'NO_COMPANY' if no case is active.
     */
    function updateCaseNumber() {
        const currentCaseNumber = getActiveCaseNumber();
        const currentCompanyName = currentCaseNumber ? getCompanyName() : 'NO_COMPANY';

        console.log(`${LOG_PREFIX} Current Case Number: ${currentCaseNumber}`);
        console.log(`${LOG_PREFIX} Current Company Name: ${currentCompanyName}`);
        console.log(`${LOG_PREFIX} Last Case Number: ${lastCaseNumber}`);
        console.log(`${LOG_PREFIX} Last Company Name: ${lastCompanyName}`);

        if (currentCaseNumber) {
            if (currentCaseNumber !== lastCaseNumber || currentCompanyName !== lastCompanyName) {
                console.log(`${LOG_PREFIX} Active Case Number or Company Name changed.`);
                lastCaseNumber = currentCaseNumber;
                lastCompanyName = currentCompanyName;
                sendNotification(currentCaseNumber, currentCompanyName);
            } else {
                console.log(`${LOG_PREFIX} Case number and Company name unchanged.`);
            }
        } else {
            if (lastCaseNumber !== 'NO_CASE' || lastCompanyName !== 'NO_COMPANY') {
                console.log(`${LOG_PREFIX} No active case detected. Sending 'NO_CASE' and 'NO_COMPANY'.`);
                sendNoCaseAndCompany();
            } else {
                console.log(`${LOG_PREFIX} Already in 'NO_CASE' and 'NO_COMPANY' state.`);
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
                console.log(`${LOG_PREFIX} Tab hidden. Sending 'NO_CASE' and 'NO_COMPANY'.`);
                sendNoCaseAndCompany();
            } else {
                console.log(`${LOG_PREFIX} Tab visible. Updating case number.`);
                // Delay to allow Salesforce's DOM to update upon becoming visible
                setTimeout(updateCaseNumber, 1000);
            }
        });

        // Before the window unloads (e.g., tab closure)
        window.addEventListener('beforeunload', () => {
            if (lastCaseNumber !== 'NO_CASE') {
                console.log(`${LOG_PREFIX} Before unload: Sending 'NO_CASE' and 'NO_COMPANY'.`);
                sendNoCaseAndCompany();
            }
        });

        console.log(`${LOG_PREFIX} Event listeners initialized.`);
    }

    /**
     * Initializes a MutationObserver to detect changes in the DOM.
     * This is useful for Single Page Applications like Salesforce.
     */
    function initMutationObserver() {
        let debounceTimer;
        const observer = new MutationObserver(() => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(updateCaseNumber, 500); // Debounce to prevent rapid calls
        });

        observer.observe(document.body, { childList: true, subtree: true });
        console.log(`${LOG_PREFIX} MutationObserver initialized with debouncing.`);
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
