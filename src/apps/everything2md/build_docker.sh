# Build Script for Everything2MD Docker Image

# 1. Build the image
# Run this from the project root (Try_make_mcp)
docker build -f src/apps/everything2md/Dockerfile -t everything2md:latest .

# 2. Run the container (Testing)
# Interactive mode with volume mapping
# Maps C:\Users to /mnt/c/Users (Standard Docker Desktop for Windows behavior)
docker run -i --rm \
  -v "C:\Users:/mnt/c/Users" \
  -e HOST_ROOT="C:/Users" \
  -e CONTAINER_ROOT="/mnt/c/Users" \
  everything2md:latest
  
# Note:
# The MCP Client (e.g. Claude) will invoke the docker command.
# You need to configure the MCP Client to run:
# command: "docker"
# args: ["run", "-i", "--rm", "-v", "C:\\Users:/mnt/c/Users", "-e", "HOST_ROOT=C:\\Users", "-e", "CONTAINER_ROOT=/mnt/c/Users", "everything2md:latest"]
