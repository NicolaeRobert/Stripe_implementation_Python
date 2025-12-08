# Stripe Implementation in Python

## 🧩Short description:

In this project I have implemented a way to pay with Stripe that redirects the user to a success or error page after everything is done. In addition to this, I also implemented a webhook that sends a confirmation email once the payment is completed.

## 📝Description of structure:

```
stipe_implementation/
│
├──static/
│
├──templates/
│
├── venv/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── app.py
```

### 📁Project Structure:

``` static ``` - This folder contains all the CSS files.

``` templates ``` - This folder contains all the HTML files.

``` venv/ ``` - This is the virtual environment that holds all the packages necessary for running the app.

``` .env ``` - This is the file that holds the environment variables that we load in the beginning (load_dotenv()).

``` .gitignore ``` - This file says which files should be ignored when committing any change.

``` README.md ``` - This file holds the project's explanation.

``` requirements.txt ``` - This file has all the packages necessary for running the project. You can run a command and all the packages that are in this file will be installed.

``` app.py ``` - The main file of the project where the app is written.

# ⚙️How to run it on your machine:

Before doing the steps below, you have to install all the necessary components for MySQL to work. You also have to do some modifications so that you can connect to the SMTP server.

For this, watch the following videos:

[MySQL setup for Windows](https://www.youtube.com/watch?v=50CQoMs4vRo&list=LL&index=6&t=557s "A youtube video for this")

[MySQL setup for Mac](https://www.youtube.com/watch?v=wpGnJHb2R58 "A youtube video for this")

[How to get a mail app password generated](https://www.youtube.com/watch?v=MkLX85XU5rU "A youtube video for this")


### 1️⃣ Clone the repository

For this you should use these commands in the terminal:

```
git clone https://github.com/your-username/your-project.git
cd your-project
```

### 2️⃣ Create and activate a virtual environment

```
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install the dependencies

``` 
pip install -r requirements.txt 
```

### 4️⃣ Set up environment variables

Create a file named .env in the root folder and add your configuration, for example:

```
publishable_key = The Stripe publishable key

secret_key = The Stripe secret key

price_id = The price id of the product created in Stripe

endpoint_secret = The endpoint of the webhook (The one Stripe CLI gives to you / The one created when you set up a webhook in Stripe)

EMAIL = Your email used to send other emails

MAIL_PASSWORD = The app password

database_password = The password of the database
```

### 5️⃣ Run the application

```
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

## Test the webhook:

### 1️⃣ Install the Stripe CLI

In order to be able to use Stripe CLI you have to install it. Follow the instructions from the next link:

[Link for installing](https://docs.stripe.com/stripe-cli/install "Stripe documentation for installing the CLI")


### 2️⃣ Make small changes for testing:

Because this is not a real-life call from Stripe to our webhook, it will leave some fields unfilled.

In order for the test to work please change ``` event["receipt_email"] ``` from lines 147 and 154 with an email that you want to use for testing, where you will also receive the confirmation email.

Now that you have changed these we can proceed:

#### 🔸 First step:

If you haven't logged in, you should do it now. Run the next command in your command prompt and it will open a page in the browser where you can connect:

```
stripe login
```

#### 🔸 Step two:

Run the next command in the command prompt:

```
stripe listen --forward-to 175.0.0.1:5000/webhooks
```

You should see something like this:

```
Ready! Your webhook signing secret is '{{WEBHOOK_SIGNING_SECRET}}' (^C to quit)
```

Copy ``` WEBHOOK_SIGNING_SECRET ``` and paste it as the value for the ``` endpoint_secret ``` variable in the .env file.

#### 🔸 Third step:

Now that you have the listener activated you can initialize some tests. Open another command prompt window and run this:

```
stripe trigger payment_intent.succeeded
```

Now if you look in the first command prompt window or in the terminal of the app you should see more calls from the Stripe CLI to the webhook and the same number of 200 responses from the webhook to Stripe CLI.

Check your email introduced instead of ``` event["receipt_email"] ``` and you should see a confirmation email sent to you.

# Conclusion:

This is a test project designed to deepen my understanding of Stripe’s payment ecosystem. Throughout the project, I explored how Stripe’s core features work, experimented with implementing and handling webhooks, and gained hands-on experience that helped translate theoretical concepts into practical knowledge. It served as a valuable learning environment for integrating real-world payment workflows into an application.
