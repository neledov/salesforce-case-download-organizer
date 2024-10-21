// ==UserScript==
// @name         Salesforce Case Number Notifier
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Sends the active case number to a local server when it changes
// @author
// @match        *://*.lightning.force.com/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    let lastCaseNumber = null;

    function sendCaseNumber(caseNumber) {
        try {
            GM_xmlhttpRequest({
                method: 'POST',
                url: 'http://localhost:8000',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: JSON.stringify({ case_number: caseNumber }),
                timeout: 5000, // Timeout in milliseconds
                onload: function(response) {
                    console.log('Case number sent:', caseNumber);
                },
                onerror: function(error) {
                    console.error('Error sending case number:', error);
                },
                ontimeout: function() {
                    console.error('Request timed out while sending case number.');
                }
            });
        } catch (e) {
            console.error('Exception in sendCaseNumber:', e);
        }
    }

    function updateCaseNumber() {
        try {
            // Find the active tab
            const activeTab = document.querySelector('a[role="tab"][aria-selected="true"][title*="| Case"]');
            if (activeTab) {
                // Extract the case number from the title attribute
                const titleAttr = activeTab.getAttribute('title');
                const match = titleAttr.match(/^(\d+)\s*\|\s*Case$/);
                if (match && match[1]) {
                    const caseNumber = match[1];
                    if (caseNumber !== lastCaseNumber) {
                        console.log('Active Case Number changed:', caseNumber);
                        lastCaseNumber = caseNumber;
                        // Send the case number to the local server
                        sendCaseNumber(caseNumber);
                    }
                } else {
                    console.warn('Case number not found in the active tab title.');
                }
            } else {
                console.warn('Active case tab not found.');
            }
        } catch (e) {
            console.error('Exception in updateCaseNumber:', e);
        }
    }

    // Initial call
    updateCaseNumber();

    // Observe changes to detect tab switches
    const observer = new MutationObserver(() => {
        updateCaseNumber();
    });

    try {
        observer.observe(document.body, { childList: true, subtree: true });
    } catch (e) {
        console.error('Exception while setting up MutationObserver:', e);
    }

    // Optional: Periodically check for case number changes
    setInterval(() => {
        updateCaseNumber();
    }, 5000); // Check every 5 seconds

})();
