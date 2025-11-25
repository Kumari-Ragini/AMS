const API_BASE = 'http://localhost:5000/api';
let videoStream = null;
let capturedImageData = null;

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const captureBtn = document.getElementById('captureBtn');
const enrollBtn = document.getElementById('enrollBtn');
const enrollForm = document.getElementById('enrollForm');

// Start Camera
startCameraBtn.addEventListener('click', async () => {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = videoStream;
        captureBtn.disabled = false;
        startCameraBtn.textContent = 'Camera Active';
        startCameraBtn.disabled = true;
    } catch (error) {
        alert('Unable to access camera: ' + error.message);
    }
});

// Capture Photo
captureBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    capturedImageData = canvas.toDataURL('image/jpeg');
    
    const preview = document.getElementById('preview');
    preview.src = capturedImageData;
    document.getElementById('capturedImage').style.display = 'block';
    
    enrollBtn.disabled = false;
    
    // Stop camera
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
});

// Enroll Student
enrollForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!capturedImageData) {
        alert('Please capture a photo first');
        return;
    }
    
    const formData = {
        student_id: document.getElementById('studentId').value,
        name: document.getElementById('studentName').value,
        department: document.getElementById('department').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        image: capturedImageData
    };
    
    enrollBtn.disabled = true;
    enrollBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enrolling...';
    
    try {
        const response = await fetch(`${API_BASE}/enroll/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Student enrolled successfully!');
            enrollForm.reset();
            document.getElementById('capturedImage').style.display = 'none';
            capturedImageData = null;
            startCameraBtn.disabled = false;
            startCameraBtn.textContent = 'Start Camera';
        } else {
            alert('Enrollment failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        enrollBtn.disabled = false;
        enrollBtn.textContent = 'Enroll Student';
    }
});