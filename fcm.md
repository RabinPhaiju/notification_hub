# Firebase In-app Messaging - https://firebase.google.com/docs/in-app-messaging

# Push notification
Push Notifications 

- Topic(tags) can be any interests/blog/news/region/ prefs (signup process interests)
- Assign tags/topic - register or any app’s lifecycle or from server
——————————————————————————————————————————
Individual push_notification through - model.notify() - with settings
For topic based notification, we cannot use our userNotificationsettngs. userNotificaitonSettings will only be used for individual messages. what if, user want to opt out, opt in from app_settings. Can we merge with out userNotification settings?

——————————————————————————————————————————
* Subscribe(un-sub) to a topic
    - Client(topic)
    - From server(token_ids,topic)

* Filter/combination of topics
    - condition: "'TopicA' in topics && ('TopicB' in topics || 'TopicC' in topics)"

* push_message format
    - messaging.Message( # both
        data={
            'score': '850',
            'time': '2:45',
        },
        notification=messaging.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        condition=condition, topic=topic,
    )
    response = messaging.send(message)

## Equivalent of push notification
fcm_device.send_message(
    data={'score': '850', 'time': '2:45'},
    title='$GOOG up 1.43% on the day',
    body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
    condition=condition, 
    topic=topic
)
-------------------------------------------------
* device group
    - create per user device group(user can have multiple devices)
    - create,add, remove device to group
    - sent notification to group same as single device (token)

--------------------------------------------------
* Manage FCM reg token #https://firebase.google.com/docs/cloud-messaging/manage-tokens
    - token associated with may be lost, destroyed, or put into storage and forgotten.
    - Retrieve registration tokens from FCM and store them on your server. 
    - An important role for the server is to keep track of each client's token and keep an updated list of active tokens. We strongly recommend implementing a token timestamp in your code and your servers, and updating this timestamp at regular intervals.
    - Maintain token freshness and remove stale tokens. In addition to removing tokens that FCM no longer considers valid, you may want to monitor other signs that tokens have become stale and remove them proactively.
    - We strongly recommend your app retrieve this token at initial startup and save it to your app server alongside a timestamp.
    - it's important to save the token to the server and update the timestamp whenever it changes, such as when:
        - The app is restored on a new device
        - The user uninstalls or re-installs the app
        - The user clears app data
        - The app becomes active again after FCM has expired its existing token
    - # token can be stored in cloud firebase or on server.

* Detect invalid token responses from the FCM backend
    - detect invalid token responses from FCM and respond by deleting from your system any registration tokens that are known to be invalid or have expired. With the HTTP v1 API, these error messages may indicate that your send request targeted invalid or expired tokens:
        - UNREGISTERED (HTTP 404) - delete token
        - INVALID_ARGUMENT (HTTP 400) - delete token
        - remove stale registration tokens from server

* update token on regular basis/periodically
    - Add server logic to update the token's timestamp at regular intervals, regardless of whether or not the token has changed. (work_manager- once a week, once a month) or on every app open or ontokenchanged()
    - There is no benefit to doing the refresh more frequently than weekly.

* best practice
    - Before sending messages to a device, ensure that the timestamp of the device's registration token is within your staleness window period.
    - remove stale tokens from the server.
    - Unsubscribe stale tokens from topics.
        - you may also want to unregister stale tokens from the topics to which they are subscribed
            1. Your app should resubscribe to topics once per month and whenever the registration token changes. This forms a self-healing solution, where the subscriptions reappear automatically when an app becomes active again.
            2. If an app instance is idle for one month (or your own staleness window) you should unsubscribe it from topics using the Firebase Admin SDK to delete the token to topic mapping from the FCM backend.
        - The benefit of these two steps is that your fanouts will occur faster since there are fewer stale tokens to fan out to, and your stale app instances will automatically resubscribe once they are active again.

* Measure delivery success
    - To get the most accurate picture of message delivery, it is best to only send messages to actively used app instances. This is especially important if you regularly send messages to topics with large numbers of subscribers; if a portion of those subscribers are actually inactive

-----------------------------------------------------------------
## You must store device groups on your server. Here's why:

FCM Doesn't Manage Groups for You: FCM provides the API to create and manage groups, but it doesn't store the association between users and their groups persistently.
Need to Track Users and Devices: You need to know which devices belong to which user to create and update groups correctly. This information is specific to your application's user management and needs to be stored in your database.
notification_key is Essential: The notification_key is how you address a group. You receive it from FCM when creating a group, and you need to store it to send messages later.
What You Need to Store:

At a minimum, you need to store the following information on your server:

User ID: A unique identifier for each user in your application.
notification_key: The key returned by FCM for a specific device group.
Mapping: A way to associate a user with their notification_key. This could be a simple table with columns like user_id and notification_key.

## Devices can be removed from a device group for various reasons, such as:
User logs out: The user signs out of your app on a specific device.
App uninstallation: The user uninstalls your app from a device.
Token refresh: The FCM registration token might be refreshed for various reasons.
Here's how you handle removing a device from a device group:

1. Detect the Removal:

Logout: When a user logs out, your app should inform your server.
Token Refresh: Your app should listen for token refresh events and send the new token to your server. If you receive a new token, it implies the old one is no longer valid.
2. Remove the Device from the Group:

Send a Request to FCM: Your server needs to make a request to the FCM API to remove the registration token from the device group.
Use the operation Parameter: In the request body, you'll use the operation parameter set to remove. You'll also need to provide the notification_key of the group and the registration token to be removed.
3. Update Your Server's Data:

Remove the Mapping: After successfully removing the device from the group via FCM, you should also update your server's database to reflect this change. Remove the association between the user and the removed registration token.
Important Considerations:

Removing All Devices: If you remove all registration tokens from a device group, FCM automatically deletes the group.
Error Handling: Implement proper error handling in your server-side code to manage cases where the removal request fails.
Token Management: Ensure you have a robust system for managing registration tokens, including handling token refresh events.

## Why immediate notification doesn't happen:

No Uninstall Callback: Neither the client-side FCM SDK nor FCM itself provides a direct callback or notification to your server when an app is uninstalled.
Token Invalidation is Delayed: FCM eventually detects that the registration token is no longer valid (because the app is gone and can't respond to messages), but this detection can take some time.
How to handle uninstalls:

Periodic Cleanup (Recommended):

Send Test Messages: Periodically (e.g., daily or weekly), send a test message to each device group.
Handle NotRegistered Errors: If you receive a NotRegistered error from FCM when sending a message to a specific registration token, it means that token is no longer valid (likely due to uninstallation).
Remove Invalid Tokens: Remove the invalid token from the device group on FCM and update your server's database.
This is the most common and reliable approach.

Token Refresh as a Clue (Less Reliable):

Expect Fewer Token Refreshes: You might observe a decrease in token refresh events from users who have uninstalled the app. However, this is not a definitive indicator, as users might simply stop using the app without uninstalling it.
Analytics and User Activity:

Track App Opens: If you're tracking app opens or other user activity, a sudden and permanent drop in activity for a specific user might suggest they've uninstalled the app.
Correlate with Token Status: You can combine this information with the periodic cleanup method to be more certain.

## you need to store the device IDs (registration tokens) along with the device group IDs (notification_key) on your server. Here's why:

Managing Group Membership: To add or remove devices from a group, you need to provide FCM with the registration tokens of the devices you want to add or remove. Without storing these tokens, you won't be able to manage the group's membership.

Periodic Cleanup: As discussed earlier, you need to periodically send test messages to each registration token in a group to detect uninstalls. To do this, you need to have a record of all the registration tokens associated with each notification_key.

Handling Token Refreshes: When a device's registration token is refreshed, you receive a new token. You need to update your stored data to reflect this change. This requires you to have the old token stored so you can replace it with the new one.

How to Store the Data:

There are several ways to structure your database to store this information. Here are two common approaches:

1. Separate Table for Device-Group Mapping:
This is generally the preferred and more scalable approach.

Users Table: Stores user information (e.g., user_id, username, etc.).
DeviceGroups Table: Stores device group information (e.g., notification_key, group_name, etc.).
DeviceGroupMembers Table: Stores the mapping between devices and groups.

2. Array of Tokens within the Device Group Record (Less Scalable):
You could store an array or list of registration tokens directly within the device group record.

## you cannot directly use filters within a topic subscription in Firebase Cloud Messaging (FCM). Topics are designed for broad, one-to-many messaging where all devices subscribed to a topic receive the message. There's no built-in mechanism to filter messages based on device properties or user attributes at the topic level.

How Topics Work (and Why Filtering Isn't Direct):

Subscription: Devices subscribe to topics (e.g., "news," "sports," "promotions").
Publish/Send: Your server sends a message to a topic.
Delivery: FCM delivers the message to all devices subscribed to that topic.
Alternatives for Achieving Filtered Messaging with Topics:

If you need to filter messages, you'll have to implement filtering logic either on the server-side before sending the message or on the client-side after receiving it.

Server-Side Filtering (Recommended for Most Cases):

Maintain User Data: Store user attributes (e.g., location, interests, language) on your server.
Send to Specific Topics Based on Filters: Instead of sending a single message to a broad topic, send messages to more granular topics based on your filters. For example, instead of a single "news" topic, you could have "news-us," "news-uk," "news-sports," etc.
Example: If you want to send a news update only to users in the US who are interested in sports, you would send the message to the "news-us-sports" topic.
This approach is generally preferred because it reduces the number of messages delivered to devices that don't need them, saving bandwidth and battery life.

Client-Side Filtering (Less Efficient):

Send to a Broader Topic: Send the message to a broader topic.
Filter on the Client: Implement logic on the client-side (in your app) to check the message payload for specific criteria and decide whether to display the notification.
This approach is less efficient because all devices subscribed to the broader topic receive the message, even if they don't meet the filter criteria.

Example Scenario (Server-Side Filtering):

Let's say you have a news app and want to send different news based on region and category.

Topics:
news-us-sports
news-uk-sports
news-us-politics
news-uk-politics
User Data: You store each user's region and interests on your server.
Sending a Message: When you have a US sports news update, you send the message to the news-us-sports topic.
Which Approach to Choose:

Server-side filtering: Use this approach whenever possible. It's more efficient and scalable.
Client-side filtering: Use this only if the filtering logic is very simple and the number of messages is low, or if server side filtering is not feasible for some reason.
In summary, while you can't filter within a topic, server-side filtering by using more granular topics is the recommended way to achieve filtered messaging with FCM topics. This ensures that only relevant messages are delivered to each device.

## the precisely the most effective and recommended way to use FCM:

Topics for Generic, Broad Messages: Use topics when you want to send the same message to a large group of users who share a common interest or characteristic. This is ideal for things like:

News updates (e.g., news-sports, news-technology)
Promotions (e.g., promotions-electronics, promotions-clothing)
General announcements or alerts
Tokens for Specific, Targeted Messages: Use tokens when you need to send messages to individual devices or a very specific subset of users based on criteria that can't be easily categorized into topics. This is suitable for:

Personalized messages (e.g., "Happy Birthday, [User Name]")
Direct replies to user actions
Messages related to a specific user's account or activity
Testing and debugging
Why this combined approach is best:

Scalability: Topics are highly scalable and efficient for broad messaging. You send one message to the topic, and FCM handles delivery to all subscribers. Sending to individual tokens becomes extremely inefficient as the number of users grows.
Efficiency: Using topics reduces the number of messages your server needs to send, saving bandwidth and server resources.
Targeting: Tokens provide precise targeting when you need to reach specific devices or users.
Flexibility: This combined approach gives you the flexibility to handle both broad and targeted messaging effectively.

## If you have 2000 users and you're considering sending messages based on individual tokens, it's crucial to understand the implications and best practices.

The Problem with Sending to 2000 Individual Tokens Directly:

Inefficiency: Sending a single message to 2000 individual tokens requires your server to make a large request to FCM with all 2000 tokens in the registration_ids array. This is inefficient in terms of network traffic and processing on both your server and FCM's servers.
FCM Limits: While FCM supports sending to multiple tokens in a single request, there are limits to the number of tokens you can include in one request (currently 500). This means you would have to make multiple requests to FCM to reach all 2000 users, further increasing the overhead.
Scalability Issues: As your user base grows beyond 2000, this approach becomes increasingly unsustainable.
Better Alternatives:

Topics (If Applicable):

Categorize Users: If there are any common interests or characteristics among these 2000 users, categorize them into topics.
Example: If these users are all interested in "sports," create a sports topic and subscribe them to it. Then, you can send a single message to the sports topic.
Combining Topics and Token-Based Messaging:

Use Topics for Broad Messages: Use topics for general announcements or messages that are relevant to a large portion of these 2000 users.
Use Tokens for Targeted Messages: Use tokens for personalized messages or messages that are only relevant to a small subset of these users.
Batching with Multicast Messaging (If Topics Aren't Suitable):

Divide into Smaller Batches: If you absolutely must send a unique message to each of the 2000 users and topics are not applicable, use multicast messaging but divide the tokens into smaller batches (e.g., batches of 500 as per FCM limit).
Make Multiple Requests: Send separate FCM requests for each batch. This is still less efficient than topics but more manageable than a single massive request.

## You need to choose the appropriate FCM messaging strategy (topics, device groups, or individual tokens) based on your specific use case and requirements. Here's a summary to help you decide:
1. Topics:

Use Case: Sending the same message to a large group of users who share a common interest or characteristic.
Key Features:
One-to-many messaging.
Efficient for broad distribution.
No need to manage individual tokens on the server for general broadcasts.
Example: Sending news updates, promotional offers, general announcements, or community-wide alerts.
2. Device Groups:

Use Case: Sending the same message to multiple devices owned by a single user.
Key Features:
Targeting all of a user's devices with a single message.
Requires server-side management of device group membership and notification_keys.
Example: Sending a notification to all of a user's devices when they receive a new message, log in from a new device, or have an account update.
3. Individual Tokens (Direct Messaging):

Use Case: Sending personalized messages or messages targeted at specific devices or very small, well-defined groups.
Key Features:
Precise targeting of individual devices.
Suitable for personalized communication or actions related to a specific device.
Less efficient for large-scale messaging.
Example: Sending a direct reply to a user's message, sending a password reset email notification, sending a message to a specific device for testing purposes, or sending a notification about a purchase confirmation.

## consider the implications of user-specific notification settings (like "likes" and "comments" toggles) when using FCM topics. Directly using topics becomes problematic because topics are designed for broad subscriptions, and you can't easily filter messages within a topic based on individual user preferences.

Here's why using pure topics won't work and how to solve this:

The Problem with Pure Topics:

If you use topics like post-likes and post-comments, and a user disables "likes" notifications in their settings, they would still receive notifications if they are subscribed to the post-likes topic. There's no way to tell FCM to not send messages to a particular user within a topic.

Solutions:

Server-Side Filtering with Database Lookup (Recommended):

This is generally the most flexible and robust approach.

Maintain User Settings: Keep your NotificationSettings model to store user preferences for each notification type (likes, comments, etc.).
Query Settings Before Sending: Before sending a notification to a topic, query your database to check each user's notification settings. Only send the notification to users who have enabled the corresponding setting.
Example: When a new like occurs, you would:
Determine the relevant topic (e.g., post-likes).
Get all subscribers to the post-likes topic.
Query the NotificationSettings table to check if each subscriber has likes_enabled set to True.
Send the notification only to the users who have likes_enabled set to True.
This approach adds a database lookup for each notification event, but it provides the necessary granularity to respect user preferences.

More Granular Topics (Less Flexible, Potentially More Complex):

You could create more granular topics based on user settings, but this can quickly become unmanageable.

Example: You could have topics like post-likes-enabled, post-likes-disabled, post-comments-enabled, post-comments-disabled.
Manage Subscriptions Based on Settings: When a user changes their settings, you would need to unsubscribe them from one topic and subscribe them to another.
This approach is less recommended because:

It creates a large number of topics, making management more complex.
It requires frequent topic subscription/unsubscription operations, which can add overhead.
Client-Side Filtering (Least Recommended):

You could send all notifications to the relevant topic and then filter them on the client-side based on user settings stored locally. This is the least efficient because all devices receive the notification, even if they are not supposed to display it. It also has a potential privacy issue, as notification details are sent to the device even if the user has disabled that type of notification.

## you have user-specific notification settings (like toggles for "likes" and "comments"), using topics directly for notification types is generally not recommended. The server-side filtering approach you implemented is the better solution.

However, there might be some edge cases where topics could still be useful in addition to your existing setup, but not as the primary means of handling notification preferences.

Here are some scenarios where topics might be considered:

Post-Level Opt-Out: If you want to provide a way for users to completely opt out of all notifications for a specific post, regardless of their general notification settings, then a topic could be used.

Implementation: When a user opts out of notifications for a post (e.g., by clicking a "mute notifications" button on the post), you could unsubscribe them from a post-specific topic (e.g., post-notifications-123 where 123 is the post ID).
Sending Notifications: When sending any notification related to that post, you would send it to the post-notifications-123 topic. Users who have opted out won't receive it.
This is more efficient than checking the database for each user, but it's only useful for a complete opt-out, not for granular control over notification types.

Broad Post Categories: If you have broad categories of posts (e.g., "announcements," "discussions," "questions") and users can choose to subscribe to notifications for entire categories, then topics could be used.

Implementation: Create topics like post-announcements, post-discussions, post-questions. When a new post is created, send a notification to the relevant category topic.
User Subscriptions: Users can subscribe or unsubscribe to these category topics in their notification settings.
This is useful for high-level filtering, but you would still need your existing server-side filtering to handle individual notification types (likes, comments) within those categories.

System-Wide Announcements: If you need to send system-wide announcements or alerts that are relevant to all users regardless of their individual settings, then a global topic like system-announcements would be appropriate.

Why Your Current Approach is Generally Better:

Granular Control: Your current approach with the NotificationSettings model and server-side filtering provides fine-grained control over notification types. Users can choose exactly which events they want to be notified about.
Less Complexity: It avoids the complexity of managing a large number of topics and frequent subscription/unsubscription operations.
Database Efficiency: With proper indexing, database lookups for notification settings are usually efficient.

## If you have in-app notifications and email notifications in addition to push notifications, and each has its own user settings, then your current approach of server-side filtering with your NotificationSettings model becomes even more crucial and appropriate.

Here's why and how to structure it:

Why Your Approach is Essential:

Multiple Channels: You have three notification channels (push, in-app, email), each with its own delivery mechanism and potentially different content.
Granular Control: Users need to be able to control which types of events trigger notifications on each channel. For example, a user might want to receive push notifications for direct messages, in-app notifications for likes, and email notifications for weekly summaries.
Centralized Settings Management: You need a centralized way to manage these settings to avoid code duplication and ensure consistency.

## Where Topics Are Less Suitable (and Your Current Approach is Better):

Notification Types (Likes, Comments, Replies, etc.): You should not use topics to manage individual notification types like likes, comments, or replies. Your current approach of using the NotificationSettings model and server-side filtering is the correct way to handle these. It provides the granular control needed for users to choose which events they want to be notified about on each channel.

## Where Topics Could Be Useful (Optional Enhancements):

Post-Level Opt-Out (Muting Notifications for a Specific Post):

Scenario: A user wants to completely stop receiving any push notifications related to a specific post, regardless of their general notification settings.
Implementation:
Create a topic specific to each post (e.g., post-notifications-{post_id}).
When a user "mutes" a post, unsubscribe their device from that post's topic.
When sending push notifications for a post, send them to the post's topic.
Benefits: This is more efficient than querying the database for each user's settings when sending notifications for a specific post where some users have opted out.

Broad Post Categories or Interests:

Scenario: You have categories of posts (e.g., "Technology," "Travel," "Food") or user interest groups. Users can choose to subscribe to notifications for entire categories.
Implementation:
Create topics for each category (e.g., category-technology, category-travel).
Allow users to subscribe or unsubscribe to these category topics in their notification settings.
When a new post is created, send a push notification to the relevant category topic(s).
Benefits: This allows users to receive notifications for a broad range of posts they are interested in without having to subscribe to individual posts.

System-Wide Announcements or Critical Alerts:

Scenario: You need to send important announcements or alerts that should reach all users regardless of their individual notification settings (e.g., service outages, security updates).
Implementation: Use a global topic (e.g., system-alerts).
Benefits: Ensures that all users receive critical information.

## Creating a Large Number of Topics is Generally Not Ideal

I previously mentioned that creating a large number of topics is not suitable. This was in the context of using topics for every notification type (likes, comments, etc.). Managing numerous such topics would be cumbersome and inefficient.

## Token-Based Push Notifications (Direct Messaging):

Ideal Use Cases:

Personalized Messages: Messages tailored to a specific user (e.g., "Happy Birthday, [User Name]").
Transactional Notifications: Notifications related to a specific user's action or account (e.g., order confirmation, password reset, direct messages/replies, new followers).
Post/Content-Specific Notifications: Notifications related to a specific piece of content or activity within your app (e.g., new comments on a post, likes on a photo, replies to a comment). This is where your PostSubscriptions model comes in.
Small, Well-Defined Groups: If you need to notify a small, static group of users (e.g., a group of moderators), sending directly to their tokens might be acceptable.
Testing and Debugging: Sending test notifications to specific devices.
Why It's Suitable: Provides precise targeting and allows for personalized content.

Why It's Less Suitable for Large Groups: Becomes inefficient as the number of recipients increases due to the need for multiple API calls (using multicast with batching helps, but topics are still better for very large groups).

Topic-Based Push Notifications:

Ideal Use Cases:

Broadcast Messages: Sending the same message to a large audience with a shared interest or characteristic.
General Announcements: System-wide updates, news, or announcements that are relevant to all or a large portion of your users.
Category-Based Notifications: Notifying users about new content or events within specific categories (e.g., "Sports News," "Tech Updates").
Opt-In/Opt-Out for Categories: Allowing users to subscribe or unsubscribe to entire categories of notifications.
Why It's Suitable: Highly efficient for broad distribution; reduces server load and network traffic.

Why It's Less Suitable for Personalized or Targeted Messages: Doesn't allow for fine-grained targeting or personalized content. Everyone subscribed to the topic receives the same message.

## FCM topics do not automatically detect app uninstalls and remove users from topics.

Here's why and what happens:

Topic Subscriptions are Persistent (Until Unsubscribed): When a device subscribes to a topic, that subscription is stored on FCM's servers. It remains active until:

The device explicitly unsubscribes.
The app is reinstalled (a new token is generated, requiring a new subscription).
You explicitly remove the subscription from your server.
No Uninstall Callback for Topics: There's no direct mechanism for FCM to notify your server or automatically unsubscribe a device from a topic when the app is uninstalled.

What Happens After Uninstall: If a user uninstalls the app and you send a message to a topic they were subscribed to, FCM will attempt to deliver the message to the device associated with the old registration token. Since the app is no longer installed, the message will fail to be delivered. FCM will eventually mark the token as invalid (usually after a few failed delivery attempts), but this process is not immediate.

How to Handle Uninstalls with Topics:

The recommended approach is the same as for handling uninstalls when sending to individual tokens:

Periodic Cleanup:

Send Test Messages: Periodically send a test message to each topic you're using. You can send a message with a small or empty payload.
Handle NotRegistered Errors: When sending messages to a topic, FCM's response will include information about any tokens that are no longer valid (due to uninstalls or other reasons). Look for the NotRegistered error code in the response.
Unsubscribe Invalid Tokens: If you receive a NotRegistered error for a token, you should explicitly unsubscribe that token from the topic on your server.

## Unfortunately, there's no direct API in FCM to query which topics a specific user (or their device's registration token) is subscribed to. FCM doesn't maintain a readily accessible mapping of tokens to topics for retrieval.

Here's why and what you can do:

Why FCM Doesn't Provide This Directly:

Scalability: Maintaining a global index of every token and its associated topics would be a massive undertaking for FCM, especially considering the scale of its user base.
Privacy: Exposing this information directly could raise privacy concerns.
How to Determine a User's Topic Subscriptions:

Maintain Your Own Mapping (Recommended):

The most reliable way is to maintain your own database table or data structure to keep track of which users (or their tokens) are subscribed to which topics.


Update on Subscription/Unsubscription: Whenever a user subscribes or unsubscribes to a topic (on the client-side using the FCM SDK), your app should send this information to your server, and your server should update its mapping accordingly.

This approach gives you complete control and allows you to efficiently query a user's topics.

Infer from Application Logic (Less Reliable):

If you have a well-defined logic for how users subscribe to topics (e.g., users are automatically subscribed to a topic based on their profile settings), you could infer their subscriptions based on those rules. However, this approach is less flexible and can become difficult to maintain if your subscription logic changes.