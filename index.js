const fs = require("fs");
const puppeteer = require("puppeteer-extra");

const proxyUrl = "http://us.smartproxy.com:10000";
const baseUrl = "https://google.com";

const StealthPlugin = require("puppeteer-extra-plugin-stealth");
puppeteer.use(StealthPlugin());

puppeteer
    .launch({
        headless: false,
        ignoreHTTPSErrors: true,
        args: [
            `--proxy-server=${proxyUrl}`,
            "--start-fullscreen",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ]
    })
    .then(async browser => {
        const page = await browser.newPage();
	    await page.setViewport({width: 1920, height: 1080});

        await page.goto(baseUrl);
        await page.waitFor("input[name='q']");
        await page.type("input[name='q']", process.argv[2], { delay: 80 });

        await Promise.all([
            page.keyboard.press("\n"),
            page.waitForNavigation()
        ]);

        const button = await page.waitForXPath(
            "//span[contains(text(), 'More places') or contains(text(), 'More businesses')]", { timeout: 10000 }
        );

        await Promise.all([
            button.click({ delay: 50 }),
            page.waitForNavigation()
        ]);
        await page.waitFor(1000);

        const ads = await page.$x("//*[@role = 'heading' and (ancestor::div[@class='VkpGBb']//*[text() = 'Ad'])]");

        for (const ad of ads) {
            const text = await page.evaluate(node => node.innerText, ad);
            console.log(text.replace(/\n/g, " ") + "\t" + process.argv[2]);
        }

        await browser.close();
    }).catch(error => {
        process.exit();
    })
