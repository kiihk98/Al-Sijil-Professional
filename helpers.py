import asyncio
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

async def ask_questions_via_dm(bot, user, questions, timeout=300):
    """Send questions to user via DM sequentially and collect answers.
    Returns list of answers or None on timeout.
    """
    answers = []
    try:
        dm = await user.create_dm()
        for i, q in enumerate(questions[:15]):
            await dm.send(f"السؤال {i+1}: {q}")
            def check(m):
                return m.author.id == user.id and isinstance(m.channel, type(dm))
            msg = await bot.wait_for('message', check=check, timeout=timeout)
            answers.append(msg.content)
        return answers
    except asyncio.TimeoutError:
        try:
            await user.send("⏳ انتهى وقت الإجابة. أعد المحاولة لاحقاً.")
        except Exception:
            pass
        return None
