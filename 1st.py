import asyncio
import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

from agent_framework import Agent, Message, AgentResponse, AgentSession
from agent_framework.openai import OpenAIChatCompletionClient
from tools import list_files, read_file

async def handle_approvals(
        query: str,
        agent: Agent,
        session: AgentSession,
) -> AgentResponse:
    result = await agent.run(query, session=session)
    while result.user_input_requests:
        approval_messages: list[Message] = []
        for user_input_needed in result.user_input_requests:
            if user_input_needed.function_call is None:
                print("[ERROR] 审批请求没有关联的 function_call, 跳过该请求")
                continue
            print("\n" + "=" * 50)
            print("Agent 请求执行工具")
            print(f"[DEBUG] 需要用户输入Function：{user_input_needed.function_call.name}")
            print(f"[DEBUG] 需要用户输入Arguments：{user_input_needed.function_call.arguments}")
            print("=" * 50)
            user_answer:str = await asyncio.to_thread(input, "是否批准执行？[y/n]:")
            user_approval  = user_answer.strip().lower() == "y"
            if user_approval :
                print("用户已经批准，执行工具")
            else:
                print("用户拒绝执行工具")
            
            approval_messages.append( Message(
                role="user",
                contents=[user_input_needed.to_function_approval_response(user_approval)]
            ))
        result = await agent.run(approval_messages, session=session)
    return result

async def handle_approvals_streaming(
        query: str,
        agent: Agent,
        session: AgentSession,
) -> None:
    current_input: str | list[Message] = query
    has_user_input_requests = True
    while has_user_input_requests:
        has_user_input_requests = False
        user_input_requests: list[Any] = []
        async for chunk in agent.run(current_input, stream=True, session=session):
            text = getattr(chunk, "text", None)
            if text:
                print(text, end="", flush=True)
            # Collect user input requests from the stream
            if chunk.user_input_requests:
                user_input_requests.extend(chunk.user_input_requests)
        if user_input_requests:
            has_user_input_requests = True
            approval_messages: list[Message] = []
            for user_input_needed in user_input_requests:
                if user_input_needed.function_call is None:
                    print("[ERROR] 审批请求没有关联的 function_call, 跳过该请求")
                    continue
                print("\n" + "=" * 50)
                print("Agent 请求执行工具")
                print(f"[DEBUG] 需要用户输入Function：{user_input_needed.function_call.name}")
                print(f"[DEBUG] 需要用户输入Arguments：{user_input_needed.function_call.arguments}")
                print("=" * 50)
                user_answer:str = await asyncio.to_thread(input, "是否批准执行？[y/n]:")
                user_approval  = user_answer.strip().lower() == "y"
                if user_approval :
                    print("用户已经批准，执行工具")
                else:
                    print("用户拒绝执行工具")
                
                approval_messages.append( Message(
                    role="user",
                    contents=[user_input_needed.to_function_approval_response(user_approval)]
                ))
            current_input = approval_messages

async def main() -> None:
    client = OpenAIChatCompletionClient(
        base_url=os.environ.get("BASE_URL"),
        api_key=os.environ.get("API_KEY"),
        model=os.environ.get("MODEL")
    )
    agent = Agent(
        client=client,
        name="Assiatant",
        instructions="你是一个简洁、可靠的助手。",
        tools=[list_files, read_file]
    )
    session = agent.create_session()

    stream_switch  = (await asyncio.to_thread(input, "是否流式？[y/n]:")).strip().lower() == "y"
    if stream_switch:
        await handle_approvals_streaming(
            query="查看本地codes目录下的文件，并且指出他们都是什么语言的",
            agent=agent,
            session=session
        )
    else:
        result = await handle_approvals(
            query="查看本地codes目录下的文件，并且指出他们都是什么语言的",
            agent=agent,
            session=session
        )
        print(f"result.text: {result.text}")




if __name__ == "__main__":
    asyncio.run(main())
