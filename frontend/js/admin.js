const API_BASE = 'http://localhost:5000/api';

async function loadAttendance() {
    try {
        const response = await fetch(`${API_BASE}/attendance/today`);
        const records = await response.json();
        
        const tbody = document.getElementById('attendanceTable');
        
        if (records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No records found</td></tr>';
            return;
        }
        
        tbody.innerHTML = records.map(record => `
            <tr>
                <td>${record.name}</td>
                <td>${record.student_id}</td>
                <td>${record.department}</td>
                <td>${new Date(record.check_in_time).toLocaleString()}</td>
                <td>${Math.round(record.confidence * 100)}%</td>
                <td><span class="badge bg-success">${record.status}</span></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
}

function exportReport() {
    alert('Export functionality - Coming soon!');
}

// Load data on page load
loadAttendance();