const API_BASE = 'http://localhost:5000/api';
let scanStream = null;
let scanning = false;

const scanVideo = document.getElementById('scanVideo');
const scanCanvas = document.getElementById('scanCanvas');
const startScanBtn = document.getElementById('startScan');
const stopScanBtn = document.getElementById('stopScan');
const resultDiv = document.getElementById('scanResult');

startScanBtn.addEventListener('click', async () => {
    try {
        scanStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        scanVideo.srcObject = scanStream;
        scanning = true;
        
        startScanBtn.style.display = 'none';
        stopScanBtn.style.display = 'block';
        
        // Start continuous scanning
        scanInterval = setInterval(captureAndRecognize, 3000);
    } catch (error) {
        alert('Unable to access camera: ' + error.message);
    }
});

stopScanBtn.addEventListener('click', () => {
    stopScanning();
});

function stopScanning() {
    scanning = false;
    if (scanStream) {
        scanStream.getTracks().forEach(track => track.stop());
        scanVideo.srcObject = null;
    }
    if (scanInterval) {
        clearInterval(scanInterval);
    }
    startScanBtn.style.display = 'block';
    stopScanBtn.style.display = 'none';
}

async function captureAndRecognize() {
    if (!scanning) return;
    
    scanCanvas.width = scanVideo.videoWidth;
    scanCanvas.height = scanVideo.videoHeight;
    const ctx = scanCanvas.getContext('2d');
    ctx.drawImage(scanVideo, 0, 0);
    
    const imageData = scanCanvas.toDataURL('image/jpeg');
    
    try {
        const response = await fetch(`${API_BASE}/attendance/mark`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });
        
        const data = await response.json();
        
        if (data.recognized) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5>✓ Attendance Marked!</h5>
                    <p class="mb-1"><strong>Name:</strong> ${data.student.name}</p>
                    <p class="mb-1"><strong>Student ID:</strong> ${data.student.student_id}</p>
                    <p class="mb-1"><strong>Department:</strong> ${data.student.department}</p>
                    <p class="mb-1"><strong>Confidence:</strong> ${data.confidence}%</p>
                    <p class="mb-0"><strong>Time:</strong> ${data.timestamp}</p>
                </div>
            `;
            stopScanning();
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <p class="mb-0">⚠️ ${data.error}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Recognition error:', error);
    }
}