from flask import Flask, request, url_for, redirect, render_template, g
from flask_mailman import EmailMessage,Mail
from dotenv import load_dotenv
from pprint import pprint
import mysql.connector
import stripe
import os

load_dotenv()
stripe.api_key=os.getenv("secret_key")
endpoint_secret=os.getenv("endpoint_secret")

app=Flask(__name__)

app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]=os.getenv("EMAIL")
app.config["MAIL_PASSWORD"]=os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
app.config["MAIL_DEFAULT_SENDER"]=os.getenv("EMAIL")

mail=Mail(app)

def get_connection():
    if not hasattr(g,"conn"):
        g.conn=mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("database_password"),
            database="stripe_webhook"
        )
    return g.conn


def get_cursor():
    conn=get_connection()
    return conn.cursor()

def delete_old_webhooks():
    conn=get_connection()
    mycursor=get_cursor()

    mycursor.execute(
        "DELETE FROM webhook_sessions WHERE session_date < DATE_SUB(NOW(), INTERVAL 7 DAY)"
    )

    conn.commit()

    mycursor.close()

def send_email_of_success(email):
    email_message=EmailMessage(
        subject="Payment comfirmation",
        body="The payment was successfull. Thank you for choosing our service!",
        from_email=os.getenv("EMAIL"),
        to=[email],
        reply_to=[os.getenv("EMAIL")]
    )

    email_message.send()

@app.route("/",methods=["GET","POST"])
def first_page():
    if request.method=="POST":
        price_id=os.getenv("price_id")

        checkout_session=stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            mode="payment",
            success_url=url_for("success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("error", _external=True) + "?session_id={CHECKOUT_SESSION_ID}"
        )

        return redirect(checkout_session.url)
    
    return render_template("first_page.html")

@app.route("/success")
def success():
    return render_template("success_page.html")

@app.route("/error")
def error():
    return render_template("error.html")

@app.route('/webhook', methods=["POST"])
def stripe_webhook():

    delete_old_webhooks()

    body=request.data
    stripe_signature=request.headers.get('Stripe-Signature')

    try:
        event=stripe.Webhook.construct_event(
            body,
            stripe_signature,
            endpoint_secret
        )
    except ValueError:
        return "Invalid payload",400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature",400
    

    conn=get_connection()
    mycursor=get_cursor()

    mycursor.execute("SELECT id FROM webhook_sessions WHERE id=%s",(event["id"],))
    id=mycursor.fetchone()

    if id==None and event["type"]=="payment_intent.succeeded":
        mycursor.execute(
            "INSERT INTO webhook_sessions (id,email) VALUES (%s,%s)",
            (event["id"],event["receip_email"])
        )

        conn.commit()

        send_email_of_success(event["receip_email"])


    mycursor.close()

    return "OK",200

@app.teardown_appcontext
def close_connetion(exception):
    conn=g.pop("conn",None)
    if conn is not None:
        conn.close()

if __name__=="__main__":
    app.run(debug=True)