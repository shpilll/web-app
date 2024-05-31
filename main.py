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


def change_brightness(image, percent):


    darken_factor = 1 - percent / 100
    darkened_image = np.clip(image * darken_factor, 0, 255).astype(np.uint8)

    return darkened_image


def plot_color_distribution(image_array, title):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Разделяем изображение на каналы R, G, B
    r, g, b = image_array[:, :, 0], image_array[:, :, 1], image_array[:, :, 2]

    # Рисуем гистограммы для каждого канала
    ax.hist(r.flatten(), bins=256, range=(0, 256), color='r', alpha=0.5, label='Red')
    ax.hist(g.flatten(), bins=256, range=(0, 256), color='g', alpha=0.5, label='Green')
    ax.hist(b.flatten(), bins=256, range=(0, 256), color='b', alpha=0.5, label='Blue')

    ax.set_title(title)
    ax.set_xlabel('Значение пикселя')
    ax.set_ylabel('Количество пикселей')
    ax.legend()

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
    original_image_path = os.path.join("static", "original_image.jpg")
    original_image.save(original_image_path)
    print(f"Сохранено изображение: {original_image_path}")


    original_color_distribution = plot_color_distribution(image_array, "Распределение цветов исходного изображения")

    return templates.TemplateResponse("result.html", {
        "request": request,
        "original_image": "/static/original_image.jpg",
        "original_color_distribution": original_color_distribution,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
