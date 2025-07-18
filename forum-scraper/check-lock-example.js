// Example of how to add a process lock to prevent overlapping executions

const fs = require('fs');
const path = require('path');

const LOCK_FILE = path.join(__dirname, 'refresh.lock');

function acquireLock() {
  try {
    // Check if lock file exists and process is still running
    if (fs.existsSync(LOCK_FILE)) {
      const pid = fs.readFileSync(LOCK_FILE, 'utf8');
      try {
        // Check if process is still running
        process.kill(pid, 0);
        console.log(`Another instance is already running (PID: ${pid}). Exiting.`);
        return false;
      } catch (e) {
        // Process not running, remove stale lock file
        fs.unlinkSync(LOCK_FILE);
      }
    }
    
    // Create lock file with current PID
    fs.writeFileSync(LOCK_FILE, process.pid.toString());
    return true;
  } catch (error) {
    console.error('Error acquiring lock:', error);
    return false;
  }
}

function releaseLock() {
  try {
    if (fs.existsSync(LOCK_FILE)) {
      fs.unlinkSync(LOCK_FILE);
    }
  } catch (error) {
    console.error('Error releasing lock:', error);
  }
}

// Usage in main script:
if (!acquireLock()) {
  process.exit(1);
}

// Ensure lock is released on exit
process.on('exit', releaseLock);
process.on('SIGINT', () => {
  releaseLock();
  process.exit(1);
});
process.on('SIGTERM', () => {
  releaseLock();
  process.exit(1);
});

// Your main refresh logic here...