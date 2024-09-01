"""
用 fastapi 简单写了一个接口，仅供参考使用

"""

import os
import uuid

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from demo.magic_pdf_parse_main import pdf_parse_main

app = FastAPI()

PDF_TEMP_PATH = "/tmp/pdfs"
PDF_OUTPUT_PATH = "/tmp/output"

# windows 路径示例
# PDF_TEMP_PATH = r"C:\Users\yzz\Desktop\temp_pdfs"
# PDF_OUTPUT_PATH = r"C:\Users\yzz\Desktop\temp_outputs"


async def process_env(file: UploadFile = File(...)) -> str:
    """处理上传的文件，写入到临时文件中并返回路径"""
    if not os.path.exists(PDF_TEMP_PATH):
        os.makedirs(PDF_TEMP_PATH)

    file_uuid = str(uuid.uuid4())[:8]
    extension = os.path.splitext(file.filename)[1]  # .pdf
    file_name = os.path.splitext(file.filename)[0]  # 没有 .pdf 后缀的文件名
    new_filename = f"{file_name}_{file_uuid}{extension}"  # 防止文件名重复
    temp_file_path = os.path.join(PDF_TEMP_PATH, new_filename)
    with open(temp_file_path, 'wb') as f:
        data = await file.read()
        f.write(data)
    return temp_file_path


@app.post("/pdf-parse/")
async def parse_pdf(file: UploadFile = File(...), parse_method: str = 'auto', is_output: bool = True):
    try:
        if not file.filename.endswith(".pdf"):
            return JSONResponse(status_code=415, content={"error": "file type error"})

        pdf_file_path = await process_env(file)
        content_list_data, md_data = pdf_parse_main(
            pdf_file_path,
            parse_method,
            is_json_md_dump=is_output,
            output_dir=PDF_OUTPUT_PATH if is_output else None
        )

        return JSONResponse(status_code=200,
                            content={
                                "md_data": md_data,
                                "content_list_data": content_list_data
                            })

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# 启动 API 服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
