# Use the models provided by push_notifications for storing device information:
GCMDevice: For Firebase
APNSDevice: For Apple

def register_device(request):
    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        device, created = GCMDevice.objects.get_or_create(
            registration_id=registration_id,
            defaults={"active": True}
        )
        if not created:
            device.active = True
            device.save()
        return JsonResponse({"success": True, "device_id": device.id})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

# Send Notifications to a Single Device
def send_push_notification(device_id, title, message):
    try:
        device = GCMDevice.objects.get(id=device_id)
        device.send_message({"title": title, "body": message})
        return {"success": True, "message": "Notification sent"}
    except GCMDevice.DoesNotExist:
        return {"success": False, "message": "Device not found"}

# Send Notifications to All Devices
def send_notification_to_all(title, message):
    devices = GCMDevice.objects.all()
    devices.send_message({"title": title, "body": message})

# Send Personalized Notification
def send_personalized_notification(user_id, title, message):
    try:
        # Retrieve the device by user_id
        device = GCMDevice.objects.get(user_id=user_id, active=True)

        # Create a personalized message with the user's name
        personalized_message = f"Hello {device.user_name}, {message}"

        # Send the personalized message to the device
        device.send_message({"title": title, "body": personalized_message})

        return {"success": True, "message": "Personalized notification sent"}
    
    except GCMDevice.DoesNotExist:
        return {"success": False, "error": "Device not found for the given user"}

# Sending Notifications to Multiple Users with Personalized Messages
def send_personalized_notifications_to_all(title, message):
    devices = GCMDevice.objects.filter(active=True)
    for device in devices:
        personalized_message = f"Hello {device.user_name}, {message}"
        device.send_message({"title": title, "body": personalized_message})
    return {"success": True, "message": "Personalized notifications sent to all users"}

# FCM's topic messaging does not directly allow you to send a personalized message to each device within a topic because a topic-based message is broadcasted to all devices in that topic. If you need personalized messages, you would typically have to send individual notifications to each device, even if they're subscribed to the same topic.

Possible Solution for Personalized Messages in Topic-based Notifications
While FCM doesn’t support sending individual personalized messages to each device in a topic directly, you can combine topic-based messaging with personalized data as follows:

Subscribe devices to topics.
Use a backend system to store additional user-specific data (e.g., user name) and associate it with the device token.
Send a topic-based notification to all subscribers.
Include custom data in the notification payload, which can be processed on the device side.

# Device Handles Personalization: On the client side, when the device receives the notification, it can extract the user_name from the custom data and personalize the notification message.

firebase.messaging().onMessage((payload) => {
    const userName = payload.data.user_name;
    const personalizedMessage = `Hello ${userName}, ${payload.notification.body}`;
    alert(personalizedMessage);  // Show personalized message to the user
});

# Filter Users on the Client Side
Include a custom user filter in the data payload of the notification.
Each client device can decide whether to display the notification based on the filter.

def send_notification_to_topic_with_filter(topic, title, message, target_users):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={your_fcm_server_key}",
    }
    payload = {
        "to": f"/topics/{topic}",
        "notification": {
            "title": title,
            "body": message,
        },
        "data": {
            "target_users": target_users  # Pass list of targeted users
        },
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Example Usage:
send_notification_to_topic_with_filter("news", "News Update", "Hello selected users!", ["user1", "user2"])
On the client side, each device processes the payload to determine if the notification is intended for them:

firebase.messaging().onMessage((payload) => {
    const targetUsers = JSON.parse(payload.data.target_users);
    const currentUserId = "user1";  // Example: Current logged-in user's ID

    if (targetUsers.includes(currentUserId)) {
        alert(payload.notification.body);  // Show notification
    }
});

