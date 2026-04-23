const { chromium } = require("playwright");

async function viewWebsite(url) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto(url, { timeout: 10000 });

    // Get page title
    const title = await page.title();
    console.log("Page Title:", title);

    // Get visible text content
    const bodyText = await page.textContent("body");
    console.log("\n--- Page Content ---\n");
    console.log(bodyText);

    // Get all links
    const links = await page.$$eval("a", (anchors) =>
      anchors.map((a) => ({ text: a.textContent, href: a.href })),
    );
    console.log("\n--- Links ---\n");
    links.forEach((link) => console.log(`${link.text} -> ${link.href}`));

    // Get images
    const images = await page.$$eval("img", (imgs) =>
      imgs.map((img) => ({ alt: img.alt, src: img.src })),
    );
    console.log("\n--- Images ---\n");
    images.forEach((img) =>
      console.log(`${img.alt || "No alt"} -> ${img.src}`),
    );

    // Get any console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") console.log("Console Error:", msg.text());
    });

    // Take a screenshot
    await page.screenshot({ path: "website-screenshot.png" });
    console.log("\nScreenshot saved as website-screenshot.png");
  } catch (error) {
    console.error("Error:", error.message);
  } finally {
    await browser.close();
  }
}

viewWebsite("http://localhost:8080");
