# APNS does not support sending payloads that exceed 2048 bytes (increased from 256 in 2014).
# Web Push accepts only one variable (message)
    - device = WebPushDevice.objects.get(registration_id=wp_reg_id)
    - device.send_message("You've got mail")
    - OR
    - data = json.dumps({"title": "Message Received", "message": "You've got mail"})
    - result, response = device.send_message(data)

# Firebase Cloud Messaging v1.
    # Create a FCM device
    fcm_device = GCMDevice.objects.create(registration_id="token", user=the_user)

    # Send a notification message
    fcm_device.send_message("This is a message")

    # Send a notification message with additional payload
    fcm_device.send_message("This is a enriched message", extra={"title": "Notification title", "icon": "icon_ressource"})

    # Send a notification message with additionnal payload (alternative syntax)
    fcm_device.send_message("This is a enriched message", title="Notification title", badge=6)

    # Send a notification message with extra data
    fcm_device.send_message("This is a message with data", extra={"other": "content", "misc": "data"})

    # Send a notification message with options
    fcm_device.send_message("This is a message", time_to_live=3600)

    # Send a data message only
    fcm_device.send_message(None, extra={"other": "content", "misc": "data"})

# FCM/GCM messages to topic members
    from push_notifications.gcm import send_message, dict_to_fcm_message

    # Create message object from dictonary. You can also directly create a messaging.Message object.
    message = dict_to_fcm_message({"body": "Hello members of my_topic!"})
    # First param is "None" because no Registration_id is needed, the message will be sent to all devices subscribed to the topic.
    send_message(None, message, to="/topics/my_topic")

## Notification payload

### fcm_device.send_message(message="Hello from FCM!")
    - The message itself is treated as the body of the notification. The title will be either the app name (on Android) or something similar (on iOS).
### fcm_device.send_message(title="Important Update", body="A new version is available.")
    - This will ensure that title is displayed as the title of the notification on both Android and iOS.
### fcm_device.send_message(data={"type": "new_message", "message_id": 123})
    - If you only send data using fcm_device.send_message(data={"key1": "value1", "key2": "value2"}), no notification will be displayed automatically by the system on either Android or iOS when the app is in the background or closed.

    Here's why:
    data messages are for background processing: The data payload is designed to be handled by your app's code. It's meant for sending information that your app needs to process, such as updating local data, triggering a background task, or navigating to a specific screen when the app is opened.
    No automatic UI: Unlike the message or notification payloads, the data payload does not trigger the system to display a notification in the notification tray or notification center.
    What happens when you send only data:

    App in foreground: If the app is running in the foreground, the onMessageReceived (Android) or didReceiveRemoteNotification (iOS) callback in your app will be triggered. You can then access the data payload and perform the necessary actions.
    App in background or closed: If the app is in the background or closed, the message will be delivered to the device, but no visible notification will be shown. The data will be available to your app when the user opens it. On Android, if the user interacts with a notification previously sent to open the app, the data payload of the most recent data message will be available in the intent that launches the app. On iOS, the data payload will be provided to the app when the user opens it from the app switcher or by tapping an app icon.
    Use cases for sending only data:

    **Silent updates**: You want to update your app's local data without notifying the user.
    **Background tasks**: You need to trigger a background task in your app, such as syncing data with a server.
    **Deferred actions**: You want to provide data that the app will use when the user opens it, such as navigating to a specific screen or displaying a particular piece of content.
    Example:

    * fcm_device.send_message(data={"action": "update_profile", "user_id": 123})
    In this case, your app's code would need to handle the data payload, check for the "action": "update_profile" key-value pair, and then perform the profile update.

    If you want to display a notification to the user, you must include a message (or title and body) in your FCM message. You can include both data and message if you want to display a notification and provide additional data to your app.
### fcm_device.send_message(message="New message received!", data={"type": "new_message", "message_id": 123})

### fcm_device.send_message(
        title="Special Offer",
        body="20% off all items!",
        icon="myicon",
        sound="default",
        data={"update_available": "true", "version": "1.2.3"},
        click_action="OPEN_MAIN_ACTIVITY",
        priority="high",
        time_to_live=3600,  # 1 hour,
        android_channel_id="my_channel_id" #for android 8+
    )

### Note
    - message vs. data: Use message (or title and body) for notifications that should be displayed to the user even if the app is closed. Use data for sending information that your app needs to process in the background. You can use both together.

## Platform-Specific Overrides:
    - fcm_device.send_message(
        title="Common Title",  # This can be overridden by platform-specific titles
        body="Common Body",    # This can be overridden by platform-specific bodies
        android={
            "notification": {
                "icon": "android_icon",
                "click_action": "OPEN_ANDROID_ACTIVITY",  # Android-specific
                "color": "#FF0000",
                "sound": "android_sound",
                "channel_id": "my_channel_id"
            },
        },
        apns={
            "payload": {
                "aps": {
                    "alert": {
                        "title": "iOS Specific Title",  # Overrides "Common Title"
                        "body": "iOS Specific Body",    # Overrides "Common Body"
                    },
                    "badge": 1,        # iOS-specific
                    "sound": "ios_sound"
                },
            },
        },
        data={
            "common_key": "common_value",  # Sent to both platforms
            "android_key": "android_only", #only sent to android
            "ios_key": "ios_only" #only sent to ios
        },
        time_to_live=3600,      # 1 hour (applies to both)
        priority="high",        # Applies to both
        collapse_key="my_collapse_key",  # Applies to both
        restricted_package_name="com.example.myapp", #applies to both
        #condition="'TopicA' in topics || 'TopicB' in topics", #applies to both
        #topic="my_topic" #applies to both
    )

## Notification Payload (For displaying notifications):

    title (String): The title of the notification.
    body (String): The body text of the notification.
    message (String): Shorthand for setting the body. If you provide only message, it's used as the body, and the title might default to your app name (on Android) or something similar (on iOS). It's always best to use title explicitly.
    icon (String): The notification icon (e.g., a drawable resource name on Android).
    sound (String): The sound to play when the notification arrives (e.g., "default" or a custom sound file name).
    badge (Integer or String): The badge count to display on the app icon.
    click_action (String): The action to perform when the user clicks the notification. This is often used to open a specific activity in your app (Android). On iOS, this is generally handled through deep linking or other app-specific mechanisms.
    title_loc_key (String): Used for localization of the title.
    title_loc_args (List of Strings): Arguments for formatting the localized title.
    body_loc_key (String): Used for localization of the body.
    body_loc_args (List of Strings): Arguments for formatting the localized body.
    android_channel_id (String): The Android notification channel ID (required for Android 8.0+).

## Message Options (General FCM settings):

    priority (String): The priority of the message. Can be "normal" or "high". High-priority messages are delivered more reliably but can consume more battery.
    time_to_live (Integer): The time in seconds for which the message should be kept in FCM storage if the device is offline.
    collapse_key (String): If multiple messages with the same collapse key are sent while the device is offline, only the last one is delivered when the device comes online. This is useful for preventing message flooding.
    restricted_package_name (String): Restricts message delivery to only the specified Android package name.
    dry_run (Boolean): If True, the message is not actually sent but only validated. Useful for testing.
    4. Targeting Options (How to send the message):

    These are passed to send_message as keyword arguments.

    registration_id (String): The registration token of a single device.
    registration_ids (List of Strings): A list of registration tokens for multiple devices.
    topic (String): The name of a topic to which the message should be sent.
    condition (String): A condition expression that specifies which devices should receive the message.
