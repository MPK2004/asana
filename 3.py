# for when we want to change the subtask to the one same as the main task priority 


from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ------------------- CONFIG -------------------
# It's safer to use environment variables for secrets
ACCESS_TOKEN = "XYZ" # Replace with your PAT
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
API_BASE_URL = "https://app.asana.com/api/1.0"

# ------------------------------------------------
def get_priority_field(task):
    """Return the priority field info from a task."""
    for field in task.get("custom_fields", []):
        if field.get("name", "").lower() == "priority":
            return field
    return None

def update_subtask_priority(subtask_id, priority_gid, priority_value, parent_id):
    """Update a single subtask's priority."""
    url = f"{API_BASE_URL}/tasks/{subtask_id}"
    payload = {"data": {"custom_fields": {priority_gid: priority_value}}}
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"✅ Updated subtask {subtask_id} to match parent {parent_id}")
    else:
        print(f"❌ Failed to update subtask {subtask_id}: {response.text}")

def sync_priority(parent_id, subtask_id=None):
    """Sync priority from parent to either one subtask or all subtasks."""
    # Get parent task details
    parent_task_url = f"{API_BASE_URL}/tasks/{parent_id}"
    parent_response = requests.get(parent_task_url, headers=HEADERS)

    if parent_response.status_code != 200:
        print(f"Error fetching parent task {parent_id}: {parent_response.text}")
        return

    parent_task = parent_response.json().get("data", {})
    priority_field = get_priority_field(parent_task)

    if not priority_field or not priority_field.get("enum_value"):
        print(f"⚠️ No priority field or value found on parent {parent_id}")
        return

    priority_gid = priority_field["gid"]
    priority_value = priority_field["enum_value"]["gid"]

    if subtask_id:
        # Only update one subtask (newly created)
        update_subtask_priority(subtask_id, priority_gid, priority_value, parent_id)
    else:
        # Update all subtasks
        subtasks_url = f"{API_BASE_URL}/tasks/{parent_id}/subtasks"
        subtasks_response = requests.get(subtasks_url, headers=HEADERS)
        subtasks = subtasks_response.json().get("data", [])

        for sub in subtasks:
            update_subtask_priority(sub["gid"], priority_gid, priority_value, parent_id)

# ------------------- WEBHOOK ROUTE (Corrected Logic) -------------------
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # Handle Asana handshake for webhook creation
    if "X-Hook-Secret" in request.headers:
        print("🤝 Asana webhook handshake successful!")
        return ("", 200, {"X-Hook-Secret": request.headers["X-Hook-Secret"]})
    
    # This 'else' block is the key change.
    # Now, we only try to parse JSON for actual webhook events, not the handshake.
    else:
        data = request.json
        print("Incoming webhook event:", data)

        for event in data.get("events", []):
            resource_type = event.get("resource", {}).get("resource_type")
            action = event.get("action")

            if resource_type == "task":
                task_id = event["resource"]["gid"]

                # Case 1: A new subtask was ADDED
                if action == "added":
                    parent = event.get("parent")
                    if parent and parent.get("resource_type") == "task":
                        parent_id = parent["gid"]
                        print(f"Subtask {task_id} added to parent {parent_id}. Syncing priority...")
                        sync_priority(parent_id, task_id)

                # Case 2: A task was CHANGED
                elif action == "changed":
                    task_details_url = f"{API_BASE_URL}/tasks/{task_id}?opt_fields=parent"
                    task_response = requests.get(task_details_url, headers=HEADERS).json()
                    task_data = task_response.get("data", {})

                    if task_data and task_data.get("parent") is None:
                        print(f"Parent task {task_id} changed. Syncing priority...")
                        sync_priority(task_id)
                    else:
                        print(f"Subtask {task_id} changed. Ignoring.")

        return jsonify({"status": "ok"}), 200

# ------------------- RUN FLASK -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask server running on http://127.0.0.1:{port}/")
    app.run(port=port, debug=True)