const { chromium } = require("playwright");

async function automatedTest(url) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const results = [];

  try {
    console.log(`Testing: ${url}`);
    await page.goto(url, { timeout: 10000 });

    // Test 1: Page loads successfully
    results.push({ test: "Page loads", status: "PASS" });

    // Test 2: Has a title
    const title = await page.title();
    results.push({
      test: "Has title",
      status: title ? "PASS" : "FAIL",
      details: title,
    });

    // Test 3: Has body content
    const bodyText = await page.textContent("body");
    results.push({
      test: "Has content",
      status: bodyText.length > 0 ? "PASS" : "FAIL",
    });

    // Test 4: Links work (check if they resolve)
    const links = await page.$$eval("a", (anchors) =>
      anchors.map((a) => a.href),
    );
    const workingLinks = links.filter((href) => href.startsWith("http"));
    results.push({
      test: "Has valid links",
      status: workingLinks.length > 0 ? "PASS" : "FAIL",
      details: `${workingLinks.length} links`,
    });

    // Test 5: Images have alt text
    const imagesWithoutAlt = await page.$$eval(
      "img",
      (imgs) => imgs.filter((img) => !img.alt).length,
    );
    results.push({
      test: "Images have alt text",
      status: imagesWithoutAlt === 0 ? "PASS" : "FAIL",
      details: `${imagesWithoutAlt} missing alt`,
    });

    // Test 6: Check for console errors
    let consoleErrors = 0;
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors++;
    });
    await page.reload();
    results.push({
      test: "No console errors",
      status: consoleErrors === 0 ? "PASS" : "FAIL",
    });

    // Print results
    console.log("\n=== TEST RESULTS ===\n");
    results.forEach((r) => {
      const icon = r.status === "PASS" ? "✓" : "✗";
      console.log(
        `${icon} ${r.test}: ${r.status}${r.details ? " (" + r.details + ")" : ""}`,
      );
    });

    const passed = results.filter((r) => r.status === "PASS").length;
    console.log(`\n${passed}/${results.length} tests passed`);
  } catch (error) {
    console.error("Test failed:", error.message);
  } finally {
    await browser.close();
  }
}

automatedTest("http://localhost:8080");
