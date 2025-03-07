/**
 * This is a simple Node.js script that can be used with Replit's Always On feature
 * to keep your bot running 24/7. It exposes an HTTP endpoint that can be pinged
 * by external services like UptimeRobot.
 */

const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

// Interval in milliseconds (5 minutes)
const PING_INTERVAL = 5 * 60 * 1000;

// Simple home route
app.get('/', (req, res) => {
  res.send('Always On Server is running! Your bot should be active.');
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'online',
    timestamp: new Date().toISOString()
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Always On server listening at http://localhost:${port}`);
  console.log(`Set up UptimeRobot to ping this URL to keep your bot alive!`);
});

// Function to ping our own bot's keep-alive endpoint
async function pingBot() {
  try {
    // Try to ping the Flask server running on port 8080
    const response = await axios.get('http://localhost:8080', { timeout: 10000 });
    console.log(`Successfully pinged bot: ${response.status}`);
  } catch (error) {
    console.error(`Error pinging bot: ${error.message}`);
  }
  
  // Schedule the next ping
  setTimeout(pingBot, PING_INTERVAL);
}

// Start pinging
console.log(`Will ping the bot every ${PING_INTERVAL/1000/60} minutes`);
pingBot(); 