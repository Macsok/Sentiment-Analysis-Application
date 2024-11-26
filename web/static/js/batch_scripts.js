function initializeProgressBars() {
    document.getElementById("fill1").style.height = document.getElementById("fill1").getAttribute("data-height");
    document.getElementById("fill2").style.height = document.getElementById("fill2").getAttribute("data-height");
    document.getElementById("fill3").style.height = document.getElementById("fill3").getAttribute("data-height");
    document.getElementById("fill1").style.height = 50 + "%";
    console.log("Progress bars initialized");
}

function runStream(){
    // Establish a connection to the SSE endpoint
    const eventSource = new EventSource("/stream");

    // When new data is received, update the page
    eventSource.onmessage = function(event) {
        const container = document.getElementById("output");
        // Parse the incoming JSON data
        const resultData = JSON.parse(event.data);
        // If the final message is received, close the connection

        if (resultData.is_final) {
            // Create a unique final message element
            const finalMessage = document.createElement("div");
            // finalMessage.className = "final-message";  // Add class for styling
            // finalMessage.textContent = resultData.text;  // Only display the final text
            finalMessage.innerHTML = `
            <p>All items processed!</p>
            <p style="color: #575a57;">note: The distribution of words classified into specific categories
will result in a neutral text if positive words balance out the negative ones, or if only neutral words are detected.</p>
                <h1 style="text-align: center;">Distribution of classified comments</h1>
                <div class="progress-container">
                    <div class="progress-bar" id="progress1">
                        <div class="progress-bar-fill positive_bar" id="fill1" data-height="${resultData.mean_pos * 100}%">Positive</div>
                    </div>
                    <div class="progress-bar" id="progress2">
                        <div class="progress-bar-fill negative_bar" id="fill2" data-height="${resultData.mean_neg * 100}%">Negative</div>
                    </div>
                    <div class="progress-bar" id="progress3">
                        <div class="progress-bar-fill neutral_bar" id="fill3" data-height="${resultData.mean_neu * 100}%">Neutral</div>
                    </div>
                </div>
                
            `;
            container.appendChild(finalMessage);
            // Scroll down
            window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
            initializeProgressBars();
            // Close the connection
            eventSource.close();
            return;  // Stop further processing
        }

        // Create a new div for the incoming data
        const newRow = document.createElement("div");
        newRow.className = "row";  // Add class for styling
        // Set the background color of the new row using the parsed color
        newRow.style.backgroundColor = resultData.color;
        // Insert the text content, author, and score received from the server
        newRow.innerHTML = `
            <div class="row">
                <div class="comment">
                    <strong>Comment:</strong> ${resultData.text} <br><br>
                </div>

                <div class="stats ${resultData.color_type}">
                    <span style="padding-top:10px;"><strong>Author:</strong> ${resultData.author}</span>
                    <span style="padding-top:10px;"><strong>Original language:</strong> ${resultData.language}</span>
                    <span style="padding-top:10px; padding-bottom:10px;"><strong>Score:</strong> ${resultData.compound}</span>
                </div>
            </div>
        `;
        container.appendChild(newRow);
        // Scroll down
        // window.scrollTo(0, document.body.scrollHeight);
    };

    // Handle errors (optional)
    eventSource.onerror = function(event) {
        console.error("Error receiving SSE:", event);
        eventSource.close();
    };

    document.getElementById("loading-icon").style.display = "none";
    document.getElementById("loading-text").style.display = "none";
}

function startScrapingAndStream(file) {
    const url = document.getElementById("textinput").value;
    document.getElementById("loading-icon").style.display = "inline-block";
    document.getElementById("loading-text").style.display = "block";
    fetch('/start_scraping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, file: file }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            runStream();
        } else {
            console.error("Scraping failed");
            document.getElementById("loading-icon").style.display = "none";
            document.getElementById("loading-text").style.display = "none";
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById("loading-icon").style.display = "none";
        document.getElementById("loading-text").style.display = "none";
    });
}