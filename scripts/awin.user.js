// ==UserScript==
// @name         Awin Auto-Join
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Auto-join all Awin programmes page by page
// @author       AgentMagnet
// @match        https://ui.awin.com/awin/affiliate/2919575/merchant-directory/index/tab/notJoined/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const TOTAL_KEY = 'awin_joined_total';
    const DELAY = 2000; // ms between clicks

    let total = parseInt(localStorage.getItem(TOTAL_KEY)) || 0;
    let idx = 0;
    let currentPage = parseInt(window.location.href.match(/page\/(\d+)/)[1]);

    function sleep(ms) {
        return new Promise(r => setTimeout(r, ms));
    }

    async function doJoin() {
        const btns = document.querySelectorAll('span.join-button');
        if (idx >= btns.length) {
            // Page done, go to next
            const nextPage = currentPage + 1;
            console.log('[Awin] Page ' + currentPage + ' done. Total: ' + total + '. Going to page ' + nextPage);
            localStorage.setItem('ap', nextPage);
            window.location.href = '/awin/affiliate/2919575/merchant-directory/index/tab/notJoined/page/' + nextPage;
            return;
        }

        const btn = btns[idx];
        const mid = btn.dataset.merchantid;
        idx++;

        try {
            btn.click();
            await sleep(1500);

            // Wait for modal
            const modal = document.querySelector('.modal.in, .modal.show');
            if (modal) {
                // Check terms checkbox
                const cb = document.getElementById('accepted');
                if (cb) cb.checked = true;

                // Click confirm
                const confirm = modal.querySelector('button.modal_save, .btn-primary, input[value="Unirse"]');
                if (confirm) confirm.click();
                else {
                    // Try submitting the form
                    const form = modal.querySelector('form');
                    if (form) form.submit();
                }
                await sleep(1000);
            }

            total++;
            localStorage.setItem(TOTAL_KEY, total);
            console.log('[Awin] [' + total + '] Joined ' + mid + ' (page ' + currentPage + ')');
        } catch(e) {
            console.log('[Awin] Error on ' + mid + ': ' + e.message);
        }

        // Next button after delay
        setTimeout(doJoin, DELAY);
    }

    console.log('[Awin] Starting page ' + currentPage + '...');
    setTimeout(doJoin, 2000);
})();
