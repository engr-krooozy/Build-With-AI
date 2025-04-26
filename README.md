    Task 1. Access your lab environment
You've signed into the Google Cloud console. Now you sign into Gmail.

Click Open Gmail to open the Gmail sign-in page.
Tip: Arrange the tabs in separate windows for easier viewing.

Sign in to Gmail using the Username, Username and the Password, Password.
Note: These credentials are also in the Lab details pane and were used to sign in to the Google Cloud console.
Once you're in Gmail, click Get started and close any informational windows. You should now see your Inbox.
You're all set to begin the lab activities!

    Task 2. Configure your Google Cloud environment
In this task you enable the Vertex AI API and then configure OAuth consent screen to define what Google Workspace displays to users.

Enable Vertex AI API
In Google Cloud console, in the Navigation menu, click APIs and Services > Library.

Type Vertex AI API into the Search for APIs & Services box, and then click Vertex AI API in the search results.

Click Enable to enable the API.

The API/Service Details page opens.

Configure the OAuth consent screen
In the left pane, click OAuth consent screen.

Click Get Started.

For App Information, set the following and then click Next:

App name: Gmail Sentiment Analysis with Gemini and Vertex AI
User support email: Username
For Audience, select Internal and then click Next.
For Contact Information, set Email addresses to Username and then click Next.
For Finish, agree to the Google API Services: User Data Policy, then click Continue.
Click Create.
Click Check my progress to verify the objective.
Configure the OAuth consent screen.

    Task 3. Set up the Apps Script project
In this task, you create and configure your add-on as an Apps Script project.

Get your Google Cloud project number
To get your Google Cloud project number to use when you create an Apps Script project:

In the Navigation menu (Navigation menu icon) click Cloud overview > Dashboard.

From the Project info section, record the Project number to use later in this lab.

Create an Apps Script project
In the Student Resources pane, click this link, script.google.com/ to open the Apps Script page.

Click New project to create an Apps Script project.

Name your project:

Click "Untitled project" at the upper left.
Name the project Gmail Sentiment Analysis with Gemini and Vertex AI, then click Rename.
Make the manifest file visible:

In the left pane, click Project Settings (gear icon).
Select Show 'appsscript.json' manifest file in editor.
Change your Google Cloud Platform project:

Scroll further down to the Google Cloud Platform (GCP) Project section and click Change project.
Set the GCP project number to the project number you previously recorded.
Click Set project.
Click Check my progress to verify the objective.
Create an Apps Script project.

    Task 4. Populate code files
In the left pane, click Editor (Editor icon) to open the editor window.
Follow the instructions below to update your project with the sample code.

appsscript.json
Open appsscript.json and replace its file contents 

Click Save to save your project.

Code.gs

Open Code.gs and replace its contents 

Click Save to save your project.

Task 5. Deploy the add-on
In this task you deploy the add-on, then verify the installation.

Deploy the add-on
In the title bar, click Deploy > Test deployments.

Confirm Gmail is listed for Application(s) and click Install.

Click Done.

Verify the installation
Refresh the Gmail tab. You should see an icon a67bbe37d76e4f19.png in the right pane.
Troubleshoot
If you don't see your add-on in the list, refresh the browser window.

If it's still not there, go back to the Apps Script project, uninstall the add-on from the Test deployments window, and then reinstall it.

Task 6. Run the add-on
You're ready to run the add-on! In this task you open and authorize the add-on, then generate emails to verify that the analysis works.

Still in Gmail, in the right pane, click Sentiment Analysis (a67bbe37d76e4f19.png).

When the side panel opens, click Authorize access to grant the add-on permission to run.

A consent screen opens. Select your email (Username) and click through the screens to allow access.

Once you have granted consent, the Sentiment Analysis pane opens on the right.

In the Sentiment Analysis pane, click Generate sample emails.
The add-on now generates sample emails to test the analysis. A message will be displayed once the generation has completed, which only takes a few seconds.

Wait for the sample emails to show-up in your inbox. You may have to refresh your inbox to see the new emails.

Once the sample emails are in your inbox, in the Sentiment Analysis pane, click Analyze emails.

A message that the analysis has been completed shows on the bottom of the add-on screen.

Note :Analyzing emails can take a while. You can refresh the page to check the status of applied labels.
The add-on analyzes your emails and applies the appropriate label ("HAPPY TONE 😊", "UPSET TONE 😡" or "NEUTRAL TONE 😐") to messages in your inbox.

You may have to refresh your Gmail to see the applied labels.

Continue to Experiment You can test the add-on by sending emails with varying sentiments (positive, negative, neutral) from your lab Gmail to another lab Gmail account. External emails are not permitted. Observe how the add-on analyzes and labels each email.
NOTE: The code only pulls the last 10 emails from your inbox, but you can change that value.
Close the add-on: Once you are finished with the add-on, you can now close the add-on by clicking the X in the top right corner of the side panel.
Click Check my progress to verify the objective.
