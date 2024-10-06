// video_record.js

const video = document.getElementById('video');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const uploadBtn = document.getElementById('uploadBtn');
const playback = document.getElementById('playback');

let mediaRecorder;
let recordedBlobs = [];

// Always access the webcam
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        video.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                recordedBlobs.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const blob = new Blob(recordedBlobs, { type: 'video/webm' });
            playback.src = window.URL.createObjectURL(blob);
            uploadBtn.disabled = false;
        };
    })
    .catch(error => {
        console.error('Error accessing media devices.', error);
        alert('Could not access your camera and microphone. Please check permissions.');
    });

startBtn.addEventListener('click', () => {
    console.log('Start button clicked');
    recordedBlobs = [];
    mediaRecorder.start();
    console.log('Recording started.');
    startBtn.disabled = true;
    stopBtn.disabled = false;
});

stopBtn.addEventListener('click', () => {
    console.log('Stop button clicked');
    mediaRecorder.stop();
    console.log('Recording stopped.');
    startBtn.disabled = false;
    stopBtn.disabled = true;
});

uploadBtn.addEventListener('click', () => {
    console.log('Upload button clicked');

    const blob = new Blob(recordedBlobs, { type: 'video/webm' });
    const formData = new FormData();
    formData.append('video', blob, 'recording.webm');  // Ensure key is 'video'

    const questionNumberMatch = window.location.pathname.match(/question(\d+)/);
    const questionNumber = questionNumberMatch ? parseInt(questionNumberMatch[1]) : null;

    if (!questionNumber) {
        alert('Could not determine the question number.');
        return;
    }

    fetch(`/save-video?question=${questionNumber}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Video uploaded successfully');

            // Determine the next action based on the current question number
            if (questionNumber < 4) {
                // Redirect to the next question
                const nextQuestionNumber = questionNumber + 1;
                window.location.href = `/question${nextQuestionNumber}`;
            } else {
                // Redirect to the debriefing page after the last question
                window.location.href = `/debriefing`;
            }
        } else {
            console.error('Upload failed:', data.error);
            alert(`Video upload failed: ${data.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        console.error('Error uploading video:', error);
        alert('An error occurred during the upload.');
    });
});
