/* ==UserScript==
// @name         Awin Auto-Join All
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Auto-join all Awin programmes
// @author       You
// @match        https://ui.awin.com/awin/affiliate/2919575/merchant-directory/index/tab/notJoined*
// @grant        none
// ==/UserScript==

(async function() {
    'use strict';
    let total = 0;
    let page = parseInt(new URLSearchParams(window.location.search).get('page')) || 1;
    const MAX_PAGES = 600;

    const sleep = ms => new Promise(r => setTimeout(r, ms));

    async function joinAllOnPage() {
        const btns = document.querySelectorAll('span.join-button');
        for (const btn of btns) {
            try {
                btn.click();
                await sleep(500);
                const cb = document.querySelector('input[type="checkbox"]');
                if (cb) cb.checked = true;
                const confirm = document.querySelector('.btn-primary');
                if (confirm) confirm.click();
                await sleep(1000);
                total++;
                console.log(`[${total}] Joined ${btn.dataset.merchantid}`);
            } catch(e) {
                console.error('Error:', e);
            }
        }
        return btns.length;
    }

    while (page <= MAX_PAGES) {
        console.log(`\n=== Page ${page} ===`);
        const count = await joinAllOnPage();
        if (count === 0) {
            console.log('No more programmes. Total:', total);
            break;
        }
        console.log(`Page ${page} done. Running total: ${total}`);
        page++;
        window.location.href = `/awin/affiliate/2919575/merchant-directory/index/tab/notJoined/page/${page}`;
        await sleep(5000); // Wait for page to load (script restarts)
    }
})();
