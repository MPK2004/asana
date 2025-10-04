Perfect Master 👑 — here’s a clean **README.md** you can drop straight into your repo:

---

````markdown
# 🔄 Asana Subtask Priority Sync

This project uses **Flask + Asana Webhooks** to automatically **sync task priority from parent tasks to their subtasks**.  
If you create a new subtask or update the parent’s priority, the subtasks will inherit the same priority value.  

---

## 🔧 Programming Language and Tools Used
- **Python 3.8+**
- **Flask** – lightweight web framework for handling webhook requests
- **Requests** – Python HTTP library to call Asana’s REST API
- **Ngrok** – to expose your local Flask server to the public internet (so Asana can reach it)
- **Asana API** – REST API for task/subtask management

---

## ⚙️ Setup Instructions

### 1. Clone or create project folder
```bash
mkdir asana-sync && cd asana-sync
````

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install flask requests
```

### 4. Get Asana Personal Access Token (PAT)

* Go to: [Asana Developer Console](https://app.asana.com/0/developer-console)
* Generate a PAT and replace it in the code:

```python
ACCESS_TOKEN = "your_asana_pat_here"
```

### 5. Run ngrok

Expose your Flask server to the internet:

```bash
ngrok http 5000
```

Copy the generated HTTPS URL (e.g., `https://xxxxx.ngrok-free.app`).

### 6. Register webhook in Asana

Create a webhook for your project or task, pointing to your ngrok URL:

```
https://xxxxx.ngrok-free.app/webhook
```

---

## ▶️ Running the Code

1. Start Flask server:

```bash
python 3.py
```

You should see:

```
🚀 Flask server running on http://127.0.0.1:5000/
```

2. Keep ngrok running in another terminal.

3. Asana will handshake automatically (`X-Hook-Secret` header handled in code).

4. Try it out:

   * Create a **subtask** → it should inherit parent’s priority.
   * Update the **parent task’s priority** → all subtasks will be updated.

---

## 📥 Expected Input / Output

### Example Input (Webhook payload from Asana)

```json
{
  "events": [
    {
      "resource": { "gid": "12345", "resource_type": "task" },
      "action": "changed"
    }
  ]
}
```

### Example Output (Flask console logs + Asana API update)

```
Incoming webhook event: { ... }
✅ Updated subtask 67890 to match parent 12345
```

---

