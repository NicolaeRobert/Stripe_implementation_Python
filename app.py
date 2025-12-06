from flask import Flask, request, url_for, redirect, render_template
from dotenv import load_dotenv
import stripe
import os

load_dotenv()
stripe.api_key=os.getenv("secret_key")

app=Flask(__name__)


@app.route("/",methods=["GET","POST"])
def first_page():
    if request.method=="POST":
        price_id="price_1SbKb8CDoTxLFO4EJVkJg6nl"

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

if __name__=="__main__":
    app.run(debug=True)