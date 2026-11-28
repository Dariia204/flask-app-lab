
import asyncio

from aiosmtpd.smtp import SMTP
from email import policy
from email.parser import BytesParser


class MailHandler:

    async def handle_DATA(self, server, session, envelope):

        message = BytesParser(
            policy=policy.default
        ).parsebytes(envelope.original_content)

        print("\n" + "=" * 60)
        print("ОТРИМАНО ЕЛЕКТРОННИЙ ЛИСТ")
        print("=" * 60)

        print(f"Від: {message['From']}")
        print(f"Кому: {message['To']}")
        print(f"Тема: {message['Subject']}")
        print("-" * 60)

        body = message.get_body(
            preferencelist=("plain",)
        )

        if body:
            print(body.get_content())

        print("=" * 60, flush=True)

        return "250 Message accepted"


async def main():

    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: SMTP(MailHandler()),
        host="127.0.0.1",
        port=1025
    )

    print("SocialSpace SMTP Server")
    print("Адреса: 127.0.0.1:1025")
    print("Очікування електронних листів...")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSMTP-сервер зупинено.")
