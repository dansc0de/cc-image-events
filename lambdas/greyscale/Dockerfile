FROM public.ecr.aws/lambda/python:3.13

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# copy requirements file
COPY pyproject.toml ${LAMBDA_TASK_ROOT}/

# install deps
RUN uv sync

# copy function code
COPY handler.py ${LAMBDA_TASK_ROOT}/

# sync the project
RUN uv sync --locked --no-install-project --no-editable

# set the CMD to your handler
CMD [ "handler.greyscale_handler" ]
