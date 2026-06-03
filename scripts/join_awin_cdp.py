"""Auto-join Awin via your existing Chrome session (fast mode)."""

import asyncio
from playwright.async_api import async_playwright

PUBLISHER_ID = 2919575
BASE = f"https://ui.awin.com/awin/affiliate/{PUBLISHER_ID}/merchant-directory/index/tab/notJoined"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        print(f"Connected! Pages: {len(await browser.contexts)}")
        
        ctx = browser.contexts[0]
        page = await ctx.new_page()
        total = 0

        for page_num in range(1, 600):
            url = f"{BASE}/page/{page_num}"
            print(f"\n--- Page {page_num} ---")
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1)

            # Remove cookie overlay
            await page.evaluate("""(() => {
                const el = document.querySelector('#usercentrics-cmp-ui');
                if (el) el.remove();
            })()""")

            btns = await page.query_selector_all("span.join-button")
            if not btns:
                print(f"Done! Total: {total}")
                break

            print(f"Found {len(btns)}")

            for btn in btns:
                try:
                    mid = await btn.get_attribute("data-merchantid")
                    await btn.click(force=True)
                    await asyncio.sleep(0.3)

                    # Check terms + confirm in modal
                    await page.evaluate("""(() => {
                        const cb = document.querySelector('input[type="checkbox"]');
                        if (cb) cb.checked = true;
                        const c = document.querySelector('.modal.in .btn-primary, .modal.show .btn-primary');
                        if (c) c.click();
                    })()""")
                    await asyncio.sleep(0.5)

                    total += 1
                    print(f"[{total}] {mid}")
                except:
                    pass

            print(f"Page done. Total: {total}")

        print(f"\nALL DONE! Joined: {total}")
        await page.close()

asyncio.run(main())
