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

## Run the web app with Docker

Build and run the image from this project directory:

```bash
docker build -t network-security-app .
docker run --rm --name network-security-app \
  --env-file .env \
  --add-host=host.docker.internal:host-gateway \
  -e FLOCI_S3_ENDPOINT_URL=http://host.docker.internal:4566 \
  -p 8000:7000 \
  network-security-app
```

Open `http://localhost:8000`. The Floci endpoint override lets the container
reach Floci running on the host. The image excludes `.env`; provide settings at
runtime as shown above. The app listens on port `7000` inside the container.

## CI/CD

The GitHub Actions workflow in `.github/workflows/main.yml` compiles the Python
sources and builds the Docker image for pull requests and pushes to `main`.
Successful pushes to `main` also publish the image to GitHub Container Registry
(`ghcr.io/<owner>/<repository>`), tagged with the commit SHA and `latest` for
the default branch. The workflow uses the repository-provided `GITHUB_TOKEN`;
enable package write access for Actions if the repository's organization policy
requires it.

After the image job succeeds on `main`, the workflow also deploys the source
using the project's `Dockerfile` to Railway. Create a Railway project and
service first, then add these GitHub repository settings under **Settings →
Secrets and variables → Actions**:

- Secret `RAILWAY_TOKEN`: a Railway project token for the target environment.
- Variables `RAILWAY_PROJECT_ID`, `RAILWAY_SERVICE_ID`, and
  `RAILWAY_ENVIRONMENT_ID`: IDs from the Railway project, service, and
  environment.

The app's tracked model files are included in the image, so Railway can use
them without connecting to local Floci. Do not set `FLOCI_S3_ENDPOINT_URL` to
`localhost` or `host.docker.internal` in Railway; those addresses refer to
your computer, not the Railway service. Configure any production S3 endpoint
and credentials as Railway service variables only if you move the models to
reachable object storage.