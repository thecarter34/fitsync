
        // WalkScape Advisor Functions
        let wsPlayerData = null;

        document.getElementById("ws-file").addEventListener("change", function(e) {
            const file = e.target.files[0];
            document.getElementById("ws-filename").textContent = file ? file.name : "";
        });

        function wsUpload() {
            const fileInput = document.getElementById("ws-file");
            const file = fileInput.files[0];
            if (!file) {
                showToast("Please select a JSON file first", "error");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            const btn = document.getElementById("ws-upload-btn");
            btn.disabled = true;
            btn.textContent = "Importing...";

            fetch("/walkscape/upload", { method: "POST", body: formData })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        wsPlayerData = result;
                        showToast("Player data imported!");
                        document.getElementById("ws-empty-state").style.display = "none";
                        document.getElementById("ws-player-info").classList.add("visible");
                        document.getElementById("ws-player-name").textContent = result.player_name;

                        const skillsGrid = document.getElementById("ws-skills-grid");
                        skillsGrid.innerHTML = "";
                        Object.entries(result.skills || {}).forEach(([name, xp]) => {
                            const badge = document.createElement("div");
                            badge.className = "ws-skill-badge";
                            badge.innerHTML = `<span class="ws-skill-name">${name}</span><span class="ws-skill-xp">${Number(xp).toLocaleString()}</span>`;
                            skillsGrid.appendChild(badge);
                        });

                        // Load saved recommendation if exists
                        loadSavedRecommendation();
                    } else {
                        showToast(result.error || "Import failed", "error");
                    }
                    btn.disabled = false;
                    btn.textContent = "Import";
                })
                .catch(e => {
                    showToast("Error: " + e.message, "error");
                    btn.disabled = false;
                    btn.textContent = "Import";
                });
        }

        function loadSavedRecommendation() {
            fetch("/walkscape_advisor")
                .then(r => r.json())
                .then(data => {
                    if (data.player && Object.keys(data.player).length > 0 && data.recommendation && data.recommendation.activity) {
                        document.getElementById("ws-recommendation").classList.add("visible");
                        document.getElementById("ws-rec-activity").textContent = data.recommendation.activity;
                        document.getElementById("ws-rec-reason").textContent = data.recommendation.reason;

                        let metaHtml = "";
                        if (data.recommendation.skill) metaHtml += `<div class="ws-rec-meta-item"><span>Skill:</span> ${data.recommendation.skill}</div>`;
                        if (data.recommendation.location) metaHtml += `<div class="ws-rec-meta-item"><span>Location:</span> ${data.recommendation.location}</div>`;
                        if (data.recommendation.est_xp) metaHtml += `<div class="ws-rec-meta-item"><span>Est. XP/action:</span> ${data.recommendation.est_xp}</div>`;
                        if (data.recommendation.why) metaHtml += `<div class="ws-rec-meta-item"><span>Why:</span> ${data.recommendation.why}</div>`;
                        document.getElementById("ws-rec-meta").innerHTML = metaHtml;
                    }
                });
        }

        function wsGetRecommendation() {
            if (!wsPlayerData) {
                showToast("Please import your player data first", "error");
                return;
            }

            const btn = document.getElementById("ws-analyze-btn");
            btn.disabled = true;
            btn.textContent = "Analyzing...";

            fetch("/walkscape/recommend", { method: "POST" })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        showToast("Context saved! I'll analyze your stats now and post the recommendation here shortly.");
                        document.getElementById("ws-recommendation").classList.add("visible");
                        document.getElementById("ws-rec-activity").textContent = "Analyzing...";
                        document.getElementById("ws-rec-reason").textContent = "I have your player context. I'll now analyze your stats, gear, and inventory against the WalkScape wiki to find the optimal next activity. Check back in a moment — I'll save the recommendation automatically.";
                        document.getElementById("ws-rec-meta").innerHTML = "";
                    } else {
                        showToast(result.error || "Failed to get context", "error");
                    }
                    btn.disabled = false;
                    btn.textContent = "Get Recommendation";
                })
                .catch(e => {
                    showToast("Error: " + e.message, "error");
                    btn.disabled = false;
                    btn.textContent = "Get Recommendation";
                });
        }
