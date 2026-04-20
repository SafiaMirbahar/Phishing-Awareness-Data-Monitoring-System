

## ⚙️ System Workflow (How It Works)

This project simulates a phishing attack scenario in a controlled environment. Below is the complete working flow from initialization to data visualization.

---

### 🔹 1. System Initialization

* The system starts by running the Flask server:

```bash
python app.py
```

* The backend server initializes:

  * Flask web application
  * Socket.IO for real-time communication
  * Session handling for multiple users

* The application becomes accessible at:

```
http://localhost:5000
```

---

### 🔹 2. Secure Tunnel Setup 

* To allow access from other devices or networks, a secure tunnel is created:

```bash
cloudflared tunnel --url http://localhost:5000
```

* This generates a public URL like:

```
https://random-name.trycloudflare.com
```

* This URL is used to simulate real-world attack scenarios across networks.

---

### 🔹 3. Dashboard Activation

* The instructor (or tester) opens the dashboard in a browser.
* The tunnel URL is configured inside the dashboard.
* A unique simulation link is generated for testing.

---

### 🔹 4. Simulation Link Generation

* The system creates a unique session ID.
* A demo link is generated such as:

```
/viewer/<session_id>
```

* This link represents a simulated phishing page.

---

### 🔹 5. User Interaction (Simulation Side)

When the link is opened:

1. A fake reward/lottery page is displayed
2. The user clicks “Claim”
3. The system shows permission requests (simulation)
4. A demo form is displayed to illustrate sensitive data input

⚠️ At this stage, the system is demonstrating how users are tricked into interacting with malicious interfaces.

---

### 🔹 6. Data Simulation & Transmission

* User actions (clicks, inputs, permissions) are captured **within the simulation**
* Data is sent to the server using Socket.IO in real-time
* Each session is tracked separately

---

### 🔹 7. Dashboard Monitoring

* The dashboard displays incoming data live:

  * Simulated user inputs
  * Activity logs
  * Session information

* This helps visualize how attackers monitor victims in real-world scenarios.

---

### 🔹 8. Session Management

* Multiple sessions can run simultaneously
* Each session is uniquely identified
* Data can be exported for analysis (JSON format)

---

### 🔹 9. End of Simulation

* Once the demonstration is complete:

  * Sessions can be cleared
  * Data should be deleted (for ethical compliance)

---

