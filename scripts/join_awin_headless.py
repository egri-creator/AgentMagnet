"""Auto-join Awin programmes via Playwright (headless, fully automated)."""

import asyncio
from playwright.async_api import async_playwright

PUBLISHER_ID = 2919575
SESSION_COOKIE = "dij2gk30a8kon85ij3a64bihvs"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        await context.add_cookies([{
            "name": "DARWINSESSIONID",
            "value": SESSION_COOKIE,
            "domain": "ui.awin.com",
            "path": "/",
        }])
        
        page = await context.new_page()
        total = 0

        for page_num in range(1, 600):
            url = f"https://ui.awin.com/awin/affiliate/{PUBLISHER_ID}/merchant-directory/index/tab/notJoined/page/{page_num}"
            print(f"\n--- Page {page_num} ---")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(5)

            if "login" in page.url.lower():
                print("Session expired")
                break

            # Dismiss cookie banner
            try:
                await page.evaluate("""
                    const ui = document.querySelector('#usercentrics-cmp-ui');
                    if (ui) ui.remove();
                """)
            except:
                pass

            # Find buttons
            buttons = await page.query_selector_all("span.join-button")
            if not buttons:
                print(f"No more. Total joined: {total}")
                break

            print(f"Found {len(buttons)} programmes")

            for btn in buttons:
                try:
                    mid = await btn.get_attribute("data-merchantid")
                    await btn.click(force=True)
                    await asyncio.sleep(0.5)

                    # Accept terms in modal
                    await page.evaluate("""
                        const cb = document.querySelector('input[type="checkbox"]');
                        if (cb) cb.checked = true;
                        const confirm = document.querySelector('.modal.in .btn-primary, .modal.show .btn-primary');
                        if (confirm) confirm.click();
                    """)
                    await asyncio.sleep(1)

                    total += 1
                    print(f"  [{total}] Joined {mid}")
                except:
                    pass

            print(f"Page {page_num} done. Total: {total}")

        print(f"\nFINISHED! Total joined: {total}")
        await browser.close()

asyncio.run(main())
