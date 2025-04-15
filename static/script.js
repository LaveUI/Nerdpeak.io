document.getElementById('tracker-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form reload

    let leetcodeUsername = document.getElementById('leetcode-username').value;
    let codeforcesUsername = document.getElementById('codeforces-username').value;

    fetch(`/dsa_tracker?leetcode=${leetcodeUsername}&codeforces=${codeforcesUsername}`)
        .then(response => response.json())
        .then(data => {
            displayStats(data);
            generateCharts(data);
        })
        .catch(error => console.error('Error:', error));
});

function displayStats(data) {
    let statsContainer = document.getElementById('stats');
    let skillsHTML = "";

    if (data.LeetCode.skills.length > 0) {
        skillsHTML = `
            <h3 class="text-lg font-bold mt-4 mb-2">LeetCode Skills:</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        `;

        data.LeetCode.skills.forEach(skill => {
            let categoryColor = skill.category === "Fundamental" ? "bg-blue-200 text-blue-700" :
                                skill.category === "Intermediate" ? "bg-yellow-200 text-yellow-700" :
                                "bg-red-200 text-red-700"; // Advanced skills in red

            skillsHTML += `
                <div class="p-3 border rounded-lg shadow-md bg-white">
                    <span class="inline-block text-xs px-2 py-1 rounded ${categoryColor}">${skill.category}</span>
                    <h4 class="text-md font-semibold mt-2">${skill.name}</h4>
                    <p class="text-sm text-gray-600">Solved: <strong>${skill.solved}</strong></p>
                </div>
            `;
        });

        skillsHTML += "</div>"; // Close grid
    }

    statsContainer.innerHTML = `
        <p class="text-lg font-bold"><strong>LeetCode:</strong> Problems Solved - ${data.LeetCode.totalSolved || "N/A"}</p>
        <p class="text-lg font-bold"><strong>Codeforces:</strong> Rating - ${data.Codeforces.rating || "N/A"} | Max Rating - ${data.Codeforces.maxRating || "N/A"}</p>
        ${skillsHTML}
    `;
}


// Store chart instances globally to destroy them before creating new ones
let leetcodeChartInstance = null;
let codeforcesChartInstance = null;

function generateCharts(data) {
    let leetcodeStats = [data.LeetCode.easySolved || 0, data.LeetCode.mediumSolved || 0, data.LeetCode.hardSolved || 0];

    // Destroy old chart instances before creating new ones
    if (leetcodeChartInstance) leetcodeChartInstance.destroy();
    if (codeforcesChartInstance) codeforcesChartInstance.destroy();

    let leetcodeChartCanvas = document.getElementById('leetcode-chart').getContext('2d');
    let codeforcesChartCanvas = document.getElementById('codeforces-chart').getContext('2d');

    leetcodeChartInstance = new Chart(leetcodeChartCanvas, {
        type: 'bar',
        data: {
            labels: ["Easy", "Medium", "Hard"],
            datasets: [{
                label: "Problems Solved",
                data: leetcodeStats,
                backgroundColor: ["green", "orange", "red"]
            }]
        }
    });

    let cfRating = data.Codeforces.rating || 0;
    let cfMaxRating = data.Codeforces.maxRating || 0;

    codeforcesChartInstance = new Chart(codeforcesChartCanvas, {
        type: 'line',
        data: {
            labels: ["Current", "Max"],
            datasets: [{
                label: "Codeforces Rating",
                data: [cfRating, cfMaxRating],
                borderColor: "blue",
                fill: false
            }]
        }
    });
}
//showing contest list

document.addEventListener("DOMContentLoaded", function () {
    fetch('/dsa_tracker')
        .then(response => response.json())
        .then(data => {
            const contestList = document.getElementById("upcomingContests");
            contestList.innerHTML = "";  // Clear previous entries
            
            if (data["Upcoming Contests"] && data["Upcoming Contests"].length > 0) {
                data["Upcoming Contests"].forEach(contest => {
                    let listItem = document.createElement("li");
                    listItem.innerHTML = `<a href="${contest.url}" target="_blank" class="text-blue-500 hover:underline">
                        ${contest.name} - ${new Date(contest.startTime * 1000).toLocaleString()}
                    </a>`;
                    contestList.appendChild(listItem);
                });
            } else {
                contestList.innerHTML = "<li>No upcoming contests found.</li>";
            }
        })
        .catch(error => console.error("Error fetching contests:", error));
});
