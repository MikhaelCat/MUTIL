import os
from openai import AsyncOpenAI
from openai import OpenAIError 

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_task_with_llm():
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": "Придумай одно короткое, странное и бессмысленное креативное задание для арт-проекта. Задание должно быть в одно предложение."}
            ],
            max_tokens=60,    
            temperature=0.0, 
            n=1, 
            stop=None    
        )
        
        if response.choices and len(response.choices) > 0 and response.choices[0].message and response.choices[0].message.content:
            task = response.choices[0].message.content.strip()
            return task
        else:
            print("OpenAI API вернул неожиданную структуру ответа или пустое содержание.")
            return None
            
    except OpenAIError as e:
        print(f"OpenAI API error (specific): {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при генерации задания LLM: {e}")
        return None

if __name__ == "__main__":
    import asyncio

    async def test_generation():
        print("Тестирование генерации задания...")
        task = await generate_task_with_llm()
        if task:
            print(f"Сгенерированное задание: {task}")
        else:
            print("Не удалось сгенерировать задание.")

    asyncio.run(test_generation())