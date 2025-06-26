# Use a Python base image (e.g., 3.12-slim-bookworm)
# This ensures Python 3.12 and a Debian Bookworm base OS
FROM python:3.12-slim-bookworm

# Install system-level dependencies required for building Prophet/PyStan
# This includes C/C++ compilers (build-essential), Fortran (gfortran),
# mathematical libraries (libopenblas-dev, liblapack-dev),
# and sometimes Java (openjdk-11-jdk) for older PyStan builds.
# pandoc is occasionally needed for documentation generation during build.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    openjdk-11-jdk \
    pkg-config \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container to your 'backend' folder
# This is where your requirements.txt and application code reside for this service
WORKDIR /app/backend

# Copy only the requirements.txt first
# This allows Docker to cache this layer, speeding up rebuilds if only code changes
COPY backend/requirements.txt .

# Install Python dependencies from requirements.txt
# --no-cache-dir reduces the image size
# --break-system-packages is a workaround for pip permission issues in slim environments
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy the rest of your backend application code into the working directory
COPY backend/ .

# Define the command to run when the container starts
# This is your existing start command for the Flask app
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:$PORT"]