# Enterprise-Grade-DataScience-Project

## Upload training artifacts to Floci S3

Floci exposes its S3-compatible API at `http://localhost:4566` in the local
setup. Configure these values in the project's ignored `.env` file:

```dotenv
FLOCI_S3_ENDPOINT_URL=http://localhost:4566
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
TRAINING_BUCKET_NAME=my-first-bucket
MODEL_S3_PREFIX=
```

You can copy `.env.example` to `.env`, then change `TRAINING_BUCKET_NAME` to
an existing bucket shown in Floci's Storage page or a new bucket name. The
training pipeline creates the bucket if it does not exist, then uploads run
artifacts under `artifacts/<run-timestamp>/` and the saved model under
`final_model/<run-timestamp>/`. If `TRAINING_BUCKET_NAME` is unset, training
continues without S3 uploads and prediction loads the local model files.

The prediction page loads `preprocessor.pkl` and `model.pkl` from the bucket.
For files uploaded at the bucket root, leave `MODEL_S3_PREFIX` empty. If the
files are inside a folder, set it to that folder name (for example,
`MODEL_S3_PREFIX=final_model/20261028_183000`). Model files are cached for
the current app process; restart the app after replacing the bucket objects.