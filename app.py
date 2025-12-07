from flask import Flask, request, url_for, redirect, render_template
from flask_mailman import EmailMessage,Mail
from dotenv import load_dotenv
from pprint import pprint
import stripe
import os
import json

load_dotenv()
stripe.api_key=os.getenv("secret_key")
endpoint_secret=os.getenv("endpoint_secret")

app=Flask(__name__)

mail=Mail()

app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]=os.getenv("EMAIL")
app.config["MAIL_PASSWORD"]=os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
app.config["MAIL_DEFAULT_SENDER"]=os.getenv("EMAIL")

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
    return "The payment was a success."

@app.route("/error")
def error():
    return "The payment failed."

@app.route('/webhook', methods=["POST"])
def stripe_webhook():
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
        return "Invalid signature",401
    

    pprint(event)

    return "OK",200


if __name__=="__main__":
    app.run(debug=True)