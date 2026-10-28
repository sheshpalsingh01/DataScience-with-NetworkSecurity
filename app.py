import os,sys
from pathlib import Path
from functools import lru_cache
import tempfile
import requests
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
from networksecurity.logging.logger import logger
from networksecurity.exception.exception import NetworkSecurityException

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, HTTPException, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.cloud.s3_sync import S3Sync

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "template"))


@lru_cache(maxsize=1)
def load_prediction_models():
    bucket_name = os.getenv("TRAINING_BUCKET_NAME")
    if bucket_name:
        prefix = os.getenv("MODEL_S3_PREFIX", "").strip("/")
        object_prefix = f"{prefix}/" if prefix else ""
        cache_dir = (
            Path(tempfile.gettempdir())
            / "networksecurity-model-cache"
            / bucket_name
            / (prefix or "root")
        )
        s3_sync = S3Sync()
        preprocessor_path = cache_dir / "preprocessor.pkl"
        model_path = cache_dir / "model.pkl"
        s3_sync.download_file(
            bucket_name,
            f"{object_prefix}preprocessor.pkl",
            str(preprocessor_path),
        )
        s3_sync.download_file(
            bucket_name,
            f"{object_prefix}model.pkl",
            str(model_path),
        )
        logger.info("Loading prediction models from S3 bucket %s", bucket_name)
    else:
        preprocessor_path = BASE_DIR / "final_model" / "preprocessor.pkl"
        model_path = BASE_DIR / "final_model" / "model.pkl"
        logger.info("TRAINING_BUCKET_NAME is unset; loading local prediction models.")

    return load_object(str(preprocessor_path)), load_object(str(model_path))


@app.get("/", tags=["authentication"])
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )

@app.get("/train")
async def train_route():
    try:
        from networksecurity.pipeline.training_pipeline import TrainingPipeline

        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        try:
            df = pd.read_csv(file.file)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as e:
            raise HTTPException(
                status_code=400,
                detail="Upload a valid, non-empty CSV file.",
            ) from e

        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded CSV has no data rows.")

        preprocessor, final_model = load_prediction_models()
        expected_columns = list(getattr(preprocessor, "feature_names_in_", []))
        if not expected_columns:
            raise RuntimeError("The saved preprocessor does not expose its expected input columns.")

        missing_columns = [column for column in expected_columns if column not in df.columns]
        extra_columns = [
            column for column in df.columns
            if column not in expected_columns and column != "Result"
        ]
        if missing_columns or extra_columns:
            problems = []
            if missing_columns:
                problems.append(f"missing columns: {', '.join(missing_columns)}")
            if extra_columns:
                problems.append(f"unexpected columns: {', '.join(extra_columns)}")
            raise HTTPException(
                status_code=400,
                detail="CSV columns do not match the model input (" + "; ".join(problems) + ").",
            )

        input_df = df[expected_columns].copy()
        invalid_columns = []
        for column in expected_columns:
            converted = pd.to_numeric(input_df[column], errors="coerce")
            if (converted.isna() & input_df[column].notna()).any():
                invalid_columns.append(column)
            input_df[column] = converted
        if invalid_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Model input columns must contain numeric values: {', '.join(invalid_columns)}.",
            )

        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        y_pred = network_model.predict(input_df)
        df["predicted_column"] = y_pred
        output_dir = BASE_DIR / "prediction_output_data"
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_dir / "output.csv", index=False)
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse(
            request=request,
            name="results.html",
            context={"request": request, "table": table_html},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction failed.")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check the server logs for details.",
        ) from e



if __name__ =="__main__":
    app_run(app,host = "0.0.0.0",port=7000,debug=True)