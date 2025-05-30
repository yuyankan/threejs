from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import uvicorn

app = FastAPI()

# 加载模型（只加载一次）
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
model.to("cpu")

@app.get("/", response_class=HTMLResponse)
async def form_get():
    return """
    <html>
        <head><title>DeepSeek 本地助手</title></head>
        <body style="font-family:sans-serif; max-width:800px; margin:auto; padding:30px;">
            <h2>DeepSeek 本地部署 (CPU)</h2>
            <form action="/" method="post">
                <label for="prompt">输入提示：</label><br>
                <textarea name="prompt" rows="5" cols="80" placeholder="请输入你的问题，例如：写一个Python快速排序算法"></textarea><br><br>
                <input type="submit" value="生成">
            </form>
        </body>
    </html>
    """

@app.post("/", response_class=HTMLResponse)
async def form_post(prompt: str = Form(...)):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=256)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return f"""
    <html>
        <head><title>DeepSeek 本地助手</title></head>
        <body style="font-family:sans-serif; max-width:800px; margin:auto; padding:30px;">
            <h2>DeepSeek 本地部署 (CPU)</h2>
            <form action="/" method="post">
                <label for="prompt">输入提示：</label><br>
                <textarea name="prompt" rows="5" cols="80">{prompt}</textarea><br><br>
                <input type="submit" value="生成">
            </form>
            <hr>
            <h3>生成结果：</h3>
            <pre style="white-space:pre-wrap;">{result}</pre>
        </body>
    </html>
    """

#if __name__ == "__main__":
    #uvicorn.run(app, port=8001)
