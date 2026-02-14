FROM ghcr.io/astral-sh/uv:python3.14-alpine

# Metadata labels <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#labelling-container-images>
LABEL org.opencontainers.image.source="https://github.com/jasonlo/prompt_sync"
LABEL org.opencontainers.image.description="A personal prompt and agent skill management system."
LABEL org.opencontainers.image.licenses="MIT"
    
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

# Install non-project dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy the application
COPY . .
RUN uv sync --locked --no-dev

# Place the venv binaries on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# TODO: Expose the application port
# TODO: Add entrypoint or CMD to run the application