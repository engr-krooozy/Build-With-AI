/*
Copyright 2024-2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Replace with your project ID
const PROJECT_ID = 'Project ID';

// Location for your Vertex AI model
const VERTEX_AI_LOCATION = 'us-east4';

// Model ID to use for sentiment analysis
const MODEL_ID = 'gemini-2.0-flash';

/**
 * Triggered when the add-on is opened from the Gmail homepage.
 *
 * @param {Object} e - The event object.
 * @returns {Card} - The homepage card.
 */
function onHomepageTrigger(e) {
  return buildHomepageCard();
}

/**
 * Builds the main card displayed on the Gmail homepage.
 *
 * @returns {Card} - The homepage card.
 */
function buildHomepageCard() {
  // Create a new card builder
  const cardBuilder = CardService.newCardBuilder();

  // Create a card header
  const cardHeader = CardService.newCardHeader();
  cardHeader.setImageUrl('https://fonts.gstatic.com/s/i/googlematerialicons/mail/v6/black-24dp/1x/gm_mail_black_24dp.png');
  cardHeader.setImageStyle(CardService.ImageStyle.CIRCLE);
  cardHeader.setTitle("Analyze your Gmail");

  // Add the header to the card
  cardBuilder.setHeader(cardHeader);

  // Create a card section
  const cardSection = CardService.newCardSection();

  // Create buttons for generating sample emails and analyzing sentiment
  const buttonSet = CardService.newButtonSet();

  // Create "Generate sample emails" button
  const generateButton = createFilledButton('Generate sample emails', 'generateSampleEmails', '#34A853');
  buttonSet.addButton(generateButton);

  // Create "Analyze emails" button
  const analyzeButton = createFilledButton('Analyze emails', 'analyzeSentiment', '#FF0000');
  buttonSet.addButton(analyzeButton);

  // Add the button set to the section
  cardSection.addWidget(buttonSet);

  // Add the section to the card
  cardBuilder.addSection(cardSection);

  // Build and return the card
  return cardBuilder.build();
}

/**
 * Creates a filled text button with the specified text, function, and color.
 *
 * @param {string} text - The text to display on the button.
 * @param {string} functionName - The name of the function to call when the button is clicked.
 * @param {string} color - The background color of the button.
 * @returns {TextButton} - The created text button.
 */
function createFilledButton(text, functionName, color) {
  // Create a new text button
  const textButton = CardService.newTextButton();

  // Set the button text
  textButton.setText(text);

  // Set the action to perform when the button is clicked
  const action = CardService.newAction();
  action.setFunctionName(functionName);
  textButton.setOnClickAction(action);

  // Set the button style to filled
  textButton.setTextButtonStyle(CardService.TextButtonStyle.FILLED);

  // Set the background color
  textButton.setBackgroundColor(color);

  return textButton;
}

/**
 * Creates a notification response with the specified text.
 *
 * @param {string} notificationText - The text to display in the notification.
 * @returns {ActionResponse} - The created action response.
 */
function buildNotificationResponse(notificationText) {
  // Create a new notification
  const notification = CardService.newNotification();
  notification.setText(notificationText);

  // Create a new action response builder
  const actionResponseBuilder = CardService.newActionResponseBuilder();

  // Set the notification for the action response
  actionResponseBuilder.setNotification(notification);

  // Build and return the action response
  return actionResponseBuilder.build();
}

/**
 * Generates sample emails for testing the sentiment analysis.
 *
 * @returns {ActionResponse} - A notification confirming email generation.
 */
function generateSampleEmails() {
  // Get the current user's email address
  const userEmail = Session.getActiveUser().getEmail();

  // Define sample emails
  const sampleEmails = [
    {
      subject: 'Thank you for amazing service!',
      body: 'Hi, I really enjoyed working with you. Thank you again!',
      name: 'Customer A'
    },
    {
      subject: 'Request for information',
      body: 'Hello, I need more information on your recent product launch. Thank you.',
      name: 'Customer B'
    },
    {
      subject: 'Complaint!',
      body: '',
      htmlBody: `<p>Hello, You are late in delivery, again.</p>
<p>Please contact me ASAP before I cancel our subscription.</p>`,
      name: 'Customer C'
    }
  ];

  // Send each sample email
  for (const email of sampleEmails) {
    GmailApp.sendEmail(userEmail, email.subject, email.body, {
      name: email.name,
      htmlBody: email.htmlBody
    });
  }

  // Return a notification
  return buildNotificationResponse("Successfully generated sample emails");
}

/**
 * Analyzes the sentiment of the first 10 threads in the inbox
 * and labels them accordingly.
 *
 * @returns {ActionResponse} - A notification confirming completion.
 */
function analyzeSentiment() {
  // Analyze and label emails
  analyzeAndLabelEmailSentiment();

  // Return a notification
  return buildNotificationResponse("Successfully completed sentiment analysis");
}

/**
 * Analyzes the sentiment of emails and applies appropriate labels.
 */
function analyzeAndLabelEmailSentiment() {
  // Define label names
  const labelNames = ["HAPPY TONE 😊", "NEUTRAL TONE 😐", "UPSET TONE 😡"];

  // Get or create labels for each sentiment
  const positiveLabel = GmailApp.getUserLabelByName(labelNames[0]) || GmailApp.createLabel(labelNames[0]);
  const neutralLabel = GmailApp.getUserLabelByName(labelNames[1]) || GmailApp.createLabel(labelNames[1]);
  const negativeLabel = GmailApp.getUserLabelByName(labelNames[2]) || GmailApp.createLabel(labelNames[2]);

  // Get the first 10 threads in the inbox
  const threads = GmailApp.getInboxThreads(0, 10);

  // Iterate through each thread
  for (const thread of threads) {
    // Iterate through each message in the thread
    const messages = thread.getMessages();
    for (const message of messages) {
      // Get the plain text body of the message
      const emailBody = message.getPlainBody();

      // Analyze the sentiment of the email body
      const sentiment = processSentiment(emailBody);

      // Apply the appropriate label based on the sentiment
      if (sentiment === 'positive') {
        thread.addLabel(positiveLabel);
      } else if (sentiment === 'neutral') {
        thread.addLabel(neutralLabel);
      } else if (sentiment === 'negative') {
        thread.addLabel(negativeLabel);
      }
    }
  }
}

/**
 * Sends the email text to Vertex AI for sentiment analysis.
 *
 * @param {string} emailText - The text of the email to analyze.
 * @returns {string} - The sentiment of the email ('positive', 'negative', or 'neutral').
 */
function processSentiment(emailText) {
  // Construct the API endpoint URL
  const apiUrl = `https://${VERTEX_AI_LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${VERTEX_AI_LOCATION}/publishers/google/models/${MODEL_ID}:generateContent`;

  // Prepare the request payload
  const payload = {
    contents: [
      {
        role: "user",
        parts: [
          {
            text: `Analyze the sentiment of the following message: ${emailText}`
          }
        ]
      }
    ],
    generationConfig: {
      temperature: 0.9,
      maxOutputTokens: 1024,
      responseMimeType: "application/json",
      // Expected response format for simpler parsing.
      responseSchema: {
        type: "object",
        properties: {
          response: {
            type: "string",
            enum: ["positive", "negative", "neutral"]
          }
        }
      }
    }
  };

  // Prepare the request options
  const options = {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${ScriptApp.getOAuthToken()}`
    },
    contentType: 'application/json',
    muteHttpExceptions: true, // Set to true to inspect the error response
    payload: JSON.stringify(payload)
  };

  // Make the API request
  const response = UrlFetchApp.fetch(apiUrl, options);

  // Parse the response. There are two levels of JSON responses to parse.
  const parsedResponse = JSON.parse(response.getContentText());
  const sentimentResponse = JSON.parse(parsedResponse.candidates[0].content.parts[0].text).response;

  // Return the sentiment
  return sentimentResponse;
}
