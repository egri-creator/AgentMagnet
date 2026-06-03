"""Auto-join Awin programmes via Playwright browser automation."""

import asyncio
from playwright.async_api import async_playwright

PUBLISHER_ID = 2919575
SESSION_COOKIE = "dij2gk30a8kon85ij3a64bihvs"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        
        await context.add_cookies([{
            "name": "DARWINSESSIONID",
            "value": SESSION_COOKIE,
            "domain": "ui.awin.com",
            "path": "/",
        }])
        
        page = await context.new_page()
        page.set_default_timeout(15000)
        total_joined = 0
        
        for page_num in range(1, 5000):
            url = f"https://ui.awin.com/awin/affiliate/{PUBLISHER_ID}/merchant-directory/index/tab/notJoined/page/{page_num}"
            print(f"\n[Page {page_num}] Loading...")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(3)
            except Exception as e:
                print(f"  Navigation error: {e}")
                # Take screenshot to debug
                await page.screenshot(path=f"error_page{page_num}.png")
                continue
            
            # Check if we're logged in
            if "login" in page.url.lower() or await page.query_selector("#login, .login-form"):
                print("  Session expired! Please re-login.")
                await page.screenshot(path="login_needed.png")
                break
            
            # Find join buttons
            buttons = await page.query_selector_all("span.join-button")
            if not buttons:
                print(f"  No more programmes to join. Total: {total_joined}")
                break
            
            print(f"  Found {len(buttons)} programmes on page {page_num}")
            
            # Dismiss cookie banner once per page
            try:
                cookie_btn = await page.query_selector('#usercentrics-cmp-ui button, [data-testid="uc-accept-all-button"], button:has-text("Accept"), button:has-text("Aceptar")')
                if cookie_btn:
                    await cookie_btn.click(force=True)
                    await asyncio.sleep(1)
            except:
                pass
            
            for btn in buttons:
                try:
                    merchant_id = await btn.get_attribute("data-merchantid")
                    name = await btn.evaluate(
                        'el => el.closest("tr")?.querySelector("td a")?.textContent?.trim() || "?"'
                    )
                    
                    await btn.click(force=True)
                    await asyncio.sleep(1.5)
                    
                    # Handle modal
                    modal = await page.query_selector(".modal.in, .modal.show, .modal.fade.in, [role=dialog]")
                    if modal:
                        # Check the terms checkbox
                        checkbox = await modal.query_selector('input[type="checkbox"]')
                        if checkbox:
                            await checkbox.check()
                            await asyncio.sleep(0.5)
                        
                        # Find confirm button
                        confirm = await modal.query_selector(
                            'button.btn-primary, input[value="Unirse"], button:has-text("Unirse")'
                        )
                        if confirm:
                            await confirm.click()
                            await asyncio.sleep(1)
                        else:
                            # Try submitting the form
                            form = await modal.query_selector("form")
                            if form:
                                await form.evaluate('f => f.submit()')
                                await asyncio.sleep(1)
                    
                    total_joined += 1
                    print(f"  [OK] [{total_joined}] {merchant_id} {name}")
                    
                except Exception as e:
                    print(f"  [ERR] {e}")
            
            print(f"  Page {page_num} done. Running total: {total_joined}")
        
        print(f"\n{'='*50}")
        print(f"  FINISHED! Total joined: {total_joined}")
        print(f"{'='*50}")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
