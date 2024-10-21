// ==UserScript==
// @name         Salesforce Active Case Number Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Extracts the case number from the active tab and updates the window title
// @author       
// @match        *://*.lightning.force.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    function updateCaseNumberInTitle() {
        // Find the active tab
        const activeTab = document.querySelector('a[role="tab"][aria-selected="true"][title*="| Case"]');
        if (activeTab) {
            // Extract the case number from the title attribute
            const titleAttr = activeTab.getAttribute('title');
            const match = titleAttr.match(/^(\d+)\s*\|\s*Case$/);
            if (match && match[1]) {
                const caseNumber = match[1];
                console.log('Active Case Number:', caseNumber);

                // Update the window title
                document.title = `Case ${caseNumber} - Salesforce`;

                // Store the case number in sessionStorage (optional)
                sessionStorage.setItem('activeCaseNumber', caseNumber);
            }
        }
    }

    // Initial call
    updateCaseNumberInTitle();

    // Observe changes to detect tab switches
    const observer = new MutationObserver((mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.attributeName === 'aria-selected') {
                updateCaseNumberInTitle();
            }
        }
    });

    // Start observing tab elements
    const tabList = document.querySelectorAll('a[role="tab"][title*="| Case"]');
    tabList.forEach(tab => {
        observer.observe(tab, { attributes: true });
    });

    // Re-scan tabs if the DOM changes
    const domObserver = new MutationObserver(() => {
        // Disconnect previous observers
        observer.disconnect();

        // Re-attach observers to updated tab elements
        const newTabList = document.querySelectorAll('a[role="tab"][title*="| Case"]');
        newTabList.forEach(tab => {
            observer.observe(tab, { attributes: true });
        });

        // Update case number in title
        updateCaseNumberInTitle();
    });

    domObserver.observe(document.body, { childList: true, subtree: true });

})();
