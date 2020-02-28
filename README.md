# python-slackapp
Slack app deployed on AWS Lambda, demonstrating how to use modals.

This app was built on top of the `slack-echo-command-python` AWS Lambda blueprint which provides a function that handles a Slack slash command and echoes the details back to the user (see this [blog post](https://aws.amazon.com/blogs/aws/new-slack-integration-blueprints-for-aws-lambda/) for more info). The blueprint has been modified to support a Python 3.8 runtime and demonstrates how to use [`views.open` to initiate a modal](https://api.slack.com/surfaces/modals/using#opening_modals).

## Environment variables
The environment variables below are encrypted at rest with the default Lambda service key. Instructions on how to encrypt keys can be found in the blueprint.

| Key        | Value           |
| ------------- |:-------------:|
| kmsEncryptedAppToken | Verification token (for Apps) used to verify that requests come from Slack |
| kmsEncryptedBotUserOAuthAccessToken | This token was automatically generated when you installed the app to your team. You can use this to authenticate your app. |
| kmsEncryptedSlashToken | This token (for Slash Commands) will be sent in the outgoing payload. You can use it to verify the request came from your Slack team. |

## Modal flow
This app implements the modal flow as described in the [understanding modal flows](https://api.slack.com/surfaces/modals/using#modal_flow) documentation page.

- [x] 1. A user interacts with an app entry point. This sends an interaction payload to the app.

- [x] 2. With the `trigger_id` from the payload, and a newly composed initial view (view A), the app uses `views.open` to initiate a modal.

- [x] 3. The user interacts with an interactive component in view A. This sends another interaction payload to the app.

- [ ] 4. The app uses the context from this new payload to update the currently visible view A with some additional content.

- [ ] 5. The user interacts with another interactive component in view A. Another interaction payload is sent to the app.

- [ ] 6. This time the app uses the context from the new payload to push a new view (view B) onto the modal's view stack, causing it to appear to the user immediately. View A remains in the view stack, but is no longer visible or active.

- [ ] 7. The user enters some values into input blocks in view B, and clicks the view's submit button. This sends a different type of interaction payload to the app.

- [ ] 8. The app handles the view submission and responds by clearing the view stack.
