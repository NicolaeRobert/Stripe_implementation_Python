from flask import Flask, request, url_for, redirect, render_template, g
from flask_mailman import EmailMessage,Mail
from dotenv import load_dotenv
from pprint import pprint
import mysql.connector
import stripe
import os


#Load the environment variables
load_dotenv()

#The stripe secret key and the endpoint of the webhook
stripe.api_key=os.getenv("secret_key")
endpoint_secret=os.getenv("endpoint_secret")

#Initialize the app
app=Flask(__name__)

#The configurations necessary for sending the email
app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]=os.getenv("EMAIL")
app.config["MAIL_PASSWORD"]=os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
app.config["MAIL_DEFAULT_SENDER"]=os.getenv("EMAIL")

#The mail instance, that helps to send the email(gets all the informations from above about the configurations created)
mail=Mail(app)

#A function that gives us the connection to the database
def get_connection():
    #Here we use the g object so that the connection is reusable and closes automatically at the end of the request(app.teardown_appcontext)
    if not hasattr(g,"conn"):
        g.conn=mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("database_password"),
            database="stripe_webhook"
        )
    return g.conn

#A function that retreives the cursor necessary for executing questies
def get_cursor():
    conn=get_connection()
    return conn.cursor()

#This is a funtion that deletes old webhook, helps to keep the database as clean as possible
def delete_old_webhooks():
    conn=get_connection()
    mycursor=get_cursor()

    mycursor.execute(
        "DELETE FROM webhook_sessions WHERE session_date < DATE_SUB(NOW(), INTERVAL 7 DAY)"
    )

    conn.commit()

    mycursor.close()

#A function that we use to send the email of confirmation from the webhook
def send_email_of_success(email):
    email_message=EmailMessage(
        subject="Payment comfirmation",
        body="The payment was successfull. Thank you for choosing our service!",
        from_email=os.getenv("EMAIL"),
        to=[email],
        reply_to=[os.getenv("EMAIL")]
    )

    email_message.send()

#The main route, that the user gets in the first instance
@app.route("/",methods=["GET","POST"])
def first_page():
    #If the method is post create the checkout object and redirect to the stripe page to pay
    if request.method=="POST":
        price_id=os.getenv("price_id")#The pride id form the stripe dashbord

        checkout_session=stripe.checkout.Session.create(
            #List of items bought by the user
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            mode="payment",#The mode id payment
            success_url=url_for("success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",#The url where stripe redirect if everything went great 
            cancel_url=url_for("error", _external=True) + "?session_id={CHECKOUT_SESSION_ID}"#The url where stripe redirect if the payment was canceled
        )

        #Redirect to stripe
        return redirect(checkout_session.url)
    
    #If the method is not post simply render the main page
    return render_template("first_page.html")

#The success page(success_url)
@app.route("/success")
def success():
    return render_template("success_page.html")

#An error page(cancel_url)
@app.route("/error")
def error():
    return render_template("error.html")

#The webhook
@app.route('/webhook', methods=["POST"])
def stripe_webhook():

    #Here we delete old webhooks
    delete_old_webhooks()

    #Get the body in binary form(that is how stripe wants it) and the stripe signature sent in the header(used for safety-to check autenticity)
    body=request.data
    stripe_signature=request.headers.get('Stripe-Signature')

    #Here we try to create the event object and treat the possible errors
    try:
        event=stripe.Webhook.construct_event(
            body,
            stripe_signature,
            endpoint_secret
        )
    except ValueError:#The ValueError is for when the body object has a problem and doesn't corespond
        return "Invalid payload",400
    except stripe.error.SignatureVerificationError:#This error is for when the stripe signature isn't matching with the one required
        return "Invalid signature",400
    

    #Here we get the connection and the cursor
    conn=get_connection()
    mycursor=get_cursor()

    #Try to take the id from the database
    mycursor.execute("SELECT id FROM webhook_sessions WHERE id=%s",(event["id"],))
    id=mycursor.fetchone()

    #If the id is none then add the id and the email to the database
    #This is necessary because stripe send multiple requests to the webhook and we want to avoid sending more than one email to the user
    if id==None and event["type"]=="payment_intent.succeeded":
        mycursor.execute(
            "INSERT INTO webhook_sessions (id,email) VALUES (%s,%s)",
            (event["id"],event["receip_email"])
        )

        #Commit the connection
        conn.commit()

        #Send the email
        send_email_of_success(event["receip_email"])

    #Clode the cursor
    mycursor.close()

    #Return 200 if everything went great
    return "OK",200

#This executes at the end of any requests(closes the connectin to the database)
@app.teardown_appcontext
def close_connetion(exception):
    conn=g.pop("conn",None)
    if conn is not None:
        conn.close()

#Execute the app
if __name__=="__main__":
    app.run(debug=True)