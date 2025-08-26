import base64
import json
from datetime import datetime
from typing import Literal, Optional

import aiofiles
from agents import function_tool, RunContextWrapper
from openai import AsyncOpenAI
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from redis_service.connect import redis
from database.repositories.user import UserRepository
from bot.utils.executed_tasks import execute_task


@function_tool
async def image_gen_tool(wrapper: RunContextWrapper, prompt: str) -> str:
    """The function generates an image at the user's request. A prompt must be provided to generate the image.

    Args:
        prompt: Prompt for image generation.
    """

    client: AsyncOpenAI = wrapper.context[0]

    img = await client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_base64 = img.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    async with aiofiles.open(f"images/image_{wrapper.context[1]}.png", "wb") as f:
        await f.write(image_bytes)

    data = {'image': f"images/image_{wrapper.context[1]}.png", 'input_tokens': img.usage.input_tokens, 'output_tokens': img.usage.output_tokens}

    await redis.set(f'image_{wrapper.context[1]}', json.dumps(data))

    return 'The image is generated'


@function_tool
async def create_task_tool(
        ctx: RunContextWrapper,
        description: str,
        agent_message: str,
        schedule_type: Literal["once", "daily", "interval"],
        time_str: Optional[str] = None,
        date_str: Optional[str] = None,
        interval_minutes: Optional[int] = None
) -> str:
    """Creates a new task in scheduler.

    Args:
        description: Task description from user
        agent_message: Message to send to main agent when executing for answer to question
        schedule_type: Schedule type (once, daily, interval)
        time_str: Time in HH:MM format for daily schedule
        date_str: Date in YYYY-MM-DD format for once schedule
        interval_minutes: Interval in minutes for interval schedule

    Returns:
        Message about task creation result
    """

    if schedule_type == "once" and not date_str:
        return "Error: date must be specified for one-time task"
    if schedule_type == "daily" and not time_str:
        return "Error: time must be specified for daily task"
    if schedule_type == "interval" and not interval_minutes:
        return "Error: interval in minutes must be specified for interval task"

    user_repo: UserRepository = ctx.context[2]
    scheduler: AsyncIOScheduler = ctx.context[3]

    task_id = await user_repo.add_task(user_id=ctx.context[1], description=description,
                                       agent_message=agent_message, schedule_type=schedule_type,
                                       time_str=time_str, date_str=date_str, interval_minutes=interval_minutes)

    if schedule_type == "once":
        if time_str:
            task_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            task_datetime = datetime.strptime(f"{date_str} 12:00", "%Y-%m-%d %H:%M")

        scheduler.add_job(
            execute_task,
            'date',
            run_date=task_datetime,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )

    elif schedule_type == "daily":
        task_time = datetime.strptime(time_str, "%H:%M").time()

        scheduler.add_job(
            execute_task,
            'cron',
            hour=task_time.hour,
            minute=task_time.minute,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )

    elif schedule_type == "interval":
        scheduler.add_job(
            execute_task,
            'interval',
            minutes=interval_minutes,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )

    return f"✅ Task successfully created!\nID: {task_id}\nDescription: {description}\nSchedule: {schedule_type}"


@function_tool
async def list_tasks_tool(
        ctx: RunContextWrapper,
) -> str:
    """Gets list of user tasks.

    Args:

    Returns:
        List of tasks in text format
    """
    user_repo: UserRepository = ctx.context[2]
    tasks = await user_repo.get_all_tasks(user_id=ctx.context[1])

    text_tasks = '\n'.join([f"Task ID[{task.id}]: {task.description}, {task.schedule_type}, "
                            f"{'active' if task.is_active else 'inactive'}, {task.time_str or task.date_str or task.interval_minutes}"
                            for task in tasks])

    return text_tasks

@function_tool
async def update_task_tool(
        ctx: RunContextWrapper,
        task_id: int,
        description: Optional[str] = None,
        agent_message: Optional[str] = None,
        schedule_type: Optional[Literal["once", "daily", "interval"]] = None,
        time_str: Optional[str] = None,
        date_str: Optional[str] = None,
        interval_minutes: Optional[int] = None,
        is_active: Optional[bool] = None
) -> str:
    """Updates existing task.

    Args:
        task_id: Task ID to update
        description: New task description
        agent_message: New agent message
        schedule_type: New schedule type
        time_str: New time in HH:MM format
        date_str: New date in YYYY-MM-DD format
        interval_minutes: New interval in minutes
        is_active: New activity status

    Returns:
        Message about update result
    """
    user_repo: UserRepository = ctx.context[2]
    scheduler: AsyncIOScheduler = ctx.context[3]

    task = await user_repo.get_task(ctx.context[1], task_id)
    if not task:
        return '❌ Task not found'

    schedule_type = schedule_type or task.schedule_type
    description = description or task.description
    agent_message = agent_message or task.agent_message
    time_str = time_str or task.time_str
    date_str = date_str or task.date_str
    interval_minutes = interval_minutes or task.interval_minutes
    is_active = is_active or task.is_active

    await user_repo.update_task(ctx.context[1], task_id, description=description,
                                agent_message=agent_message, is_active=is_active,
                                schedule_type=schedule_type, time_str=time_str,
                                date_str=date_str, interval_minutes=interval_minutes)
    try:
        scheduler.remove_job(f'{ctx.context[1]}_{task_id}')
    except:
        pass

    if schedule_type == "once":
        if time_str:
            task_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            task_datetime = datetime.strptime(f"{date_str} 12:00", "%Y-%m-%d %H:%M")

        scheduler.add_job(
            execute_task,
            'date',
            run_date=task_datetime,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )

    elif schedule_type == "daily":
        task_time = datetime.strptime(time_str, "%H:%M").time()

        scheduler.add_job(
            execute_task,
            'cron',
            hour=task_time.hour,
            minute=task_time.minute,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )

    elif schedule_type == "interval":
        scheduler.add_job(
            execute_task,
            'interval',
            minutes=interval_minutes,
            args=[ctx.context[1], task_id],
            id=f'{ctx.context[1]}_{task_id}'
        )


@function_tool
async def delete_task_tool(
        ctx: RunContextWrapper,
        task_id: int
) -> str:
    """Deletes task from scheduler.

    Args:
        task_id: Task ID to delete

    Returns:
        Message about deletion result
    """

    user_repo: UserRepository = ctx.context[2]
    scheduler: AsyncIOScheduler = ctx.context[3]
    await user_repo.delete_task(ctx.context[1], task_id)

    try:
        scheduler.remove_job(f'{ctx.context[1]}_{task_id}')
    except:
        pass

    return '✅ Task successfully deleted'



@function_tool
async def get_task_details_tool(
        ctx: RunContextWrapper,
        task_id: int
) -> str:
    """Gets detailed task information.

    Args:
        task_id: Task ID

    Returns:
        Detailed task information
    """

    user_repo: UserRepository = ctx.context[2]

    task = await user_repo.get_task(ctx.context[1], task_id)
    if not task:
        return '❌ Task not found'

    return (f'📋 Task Details\n\n' 
           f'ID: `{task.id}`\n' 
           f'Description: {task.description}\n' 
           f'Agent Message: {task.agent_message}\n'
           f'Schedule Type: {task.schedule_type}\n'
           f'Status: {"active" if task.is_active else "inactive"}' 
           f'{"Interval" if task.schedule_type == "interval" else "Date"}: {task.time_str or task.date_str or task.interval_minutes}\n')