const API_BASE = 'http://localhost:5000/api';

// Login Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    window.location.href = 'index.html';
                } else {
                    alert('Invalid credentials');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
            }
        });
    }
});

// Load Dashboard Data
async function loadDashboard() {
    try {
        // Fetch statistics
        const statsResponse = await fetch(`${API_BASE}/attendance/statistics`);
        const stats = await statsResponse.json();
        
        document.getElementById('totalStudents').textContent = stats.total_students;
        document.getElementById('presentCount').textContent = stats.present;
        document.getElementById('absentCount').textContent = stats.absent;
        document.getElementById('attendanceRate').textContent = stats.attendance_rate + '%';
        
        // Fetch recent attendance
        const attendanceResponse = await fetch(`${API_BASE}/attendance/today`);
        const attendance = await attendanceResponse.json();
        
        const container = document.getElementById('recentAttendance');
        if (attendance.length === 0) {
            container.innerHTML = '<p class="text-muted">No attendance records today</p>';
            return;
        }
        
        container.innerHTML = attendance.slice(0, 10).map(record => `
            <div class="d-flex justify-content-between align-items-center p-3 mb-2 bg-light rounded">
                <div class="d-flex align-items-center">
                    <div class="avatar-circle me-3">
                        ${record.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                        <strong>${record.name}</strong>
                        <p class="mb-0 small text-muted">
                            <span class="me-2">🕐 ${new Date(record.check_in_time).toLocaleTimeString()}</span>
                            ${record.department}
                        </p>
                    </div>
                </div>
                <span class="badge bg-success">Present</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Utility: Display message
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}