from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import uvicorn
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def change_brightness(image, factor):

    brightened_image = image + factor
    brightened_image = np.clip(brightened_image, 0, 1)

    return brightened_image



def plot_color_distribution(image_array, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(image_array.flatten(), bins=256, range=(0, 256), color='b')
    ax.set_title(title)
    ax.set_xlabel('Значение пикселя')
    ax.set_ylabel('Количество пикселей')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

@app.get("/", name="home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_image", name="process_image")
async def process_image(
    request: Request,
    image: UploadFile = File(...),
    procent_bright: int = Form(...)
):

    image_bytes = await image.read()
    image_array = np.array(Image.open(BytesIO(image_bytes)))


    image_array = change_brightness(image_array, procent_bright)


    original_image = Image.fromarray(image_array)
    original_image_path = os.path.join("static", "original_image.png")
    original_image.save(original_image_path)
    print(f"Сохранено изображение: {original_image_path}")


    original_color_distribution = plot_color_distribution(image_array, "Распределение цветов исходного изображения")

    return templates.TemplateResponse("result.html", {
        "request": request,
        "original_image": "/static/original_image.png",
        "original_color_distribution": original_color_distribution,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
