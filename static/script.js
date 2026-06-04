let mediaRecorder;

let audioChunks = [];

const recordBtn = document.getElementById("recordBtn");

const statusDiv = document.getElementById("status");

recordBtn.addEventListener("click", async () => {

    // START RECORDING
    if(recordBtn.innerText === "Start Recording"){

        let stream;

        try{

            stream = await navigator.mediaDevices.getUserMedia({
                audio:true
            });

        }
        catch(error){

            alert("Microphone permission denied!");

            console.log(error);

            return;
        }

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.start();

        audioChunks = [];

        statusDiv.innerHTML = "🎙 Recording Started...";

        recordBtn.innerText = "Stop Recording";

        mediaRecorder.ondataavailable = event => {

            audioChunks.push(event.data);

        };

    }

    // STOP RECORDING
    else{

        mediaRecorder.stop();

        statusDiv.innerHTML = "⏳ Processing Voice...";

        recordBtn.innerText = "Start Recording";

        mediaRecorder.onstop = async () => {

            const audioBlob = new Blob(audioChunks, {
                type:'audio/webm'
            });

            const formData = new FormData();

            formData.append("audio", audioBlob, "recording.webm");

            const response = await fetch("/analyze", {
                method:"POST",
                body:formData
            });

            const data = await response.json();

            console.log(data);

            const resultDiv = document.getElementById("result");

            // ERROR HANDLE
            if(data.error){

                resultDiv.innerHTML =
                `<p>${data.error}</p>`;

                return;
            }

            // SHOW RESULTS
            resultDiv.innerHTML = `

            <h2>📊 Analysis Result</h2>

            <p><strong>Speech:</strong>
            ${data.speech}</p>

            <p><strong>Emotion:</strong>
            ${data.emotion}</p>

            <p><strong>Tone:</strong>
            ${data.tone}</p>

            <p><strong>Confidence:</strong>
            ${data.confidence}</p>

            <p><strong>Stress:</strong>
            ${data.stress}</p>

            <p><strong>Feedback:</strong>
            ${data.feedback}</p>

            `;

            statusDiv.innerHTML = "✅ Analysis Complete";
        };
    }
});