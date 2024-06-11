from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse


class EmailSchema(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME ="testbezpieczni@gmail.com",
    MAIL_PASSWORD = "wzcw jobi ibyl mmoe",
    MAIL_FROM = "testbezpieczni@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# Send email with random password to user
async def simple_send(email: EmailSchema, password) -> JSONResponse:

    message = MessageSchema(
        subject="Password",
        recipients=email,
        body=f"Twoje hasło to: {password}, zaloguj się na stronie https://bezpieczni-app.onrender.com/login",
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

