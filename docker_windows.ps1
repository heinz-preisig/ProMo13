

#docker run -it -v /run/desktop/mnt/host/wslg/.X11-unix:/tmp/.X11-unix `
#               -v /run/desktop/mnt/host/wslg:/mnt/wslg `
#               -v C:\Users\heinz\CAM\Ontology_Repository:/Ontology_Repository `
#               -e DISPLAY=:0 `
#               -e WAYLAND_DISPLAY=wayland-0 `
#               -e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir `
#               -e PULSE_SERVER=/mnt/wslg/PulseServer `
#               hapdocker/promo2025

# Define Docker image and container name
# Define Docker image and container name
# Define Docker image and container name



# Define Docker image and container name
$imageName = "hapdocker/promo2025"
$containerName = "promo2025-container"

# Dynamically get the local Ontology_Repository path and convert backslashes
$userOntologyPath = Join-Path $env:USERPROFILE "CAM\Ontology_Repository"
$dockerLocalPath = $userOntologyPath -replace '\\', '/'

# Build Docker arguments as a list (safest method)
$dockerArgs = @(
    "run",
    "--name", $containerName,
    "-it",
    "--volume", "/run/desktop/mnt/host/wslg/.X11-unix:/tmp/.X11-unix",
    "--volume", "/run/desktop/mnt/host/wslg:/mnt/wslg",
    "--volume", "${dockerLocalPath}:/Ontology_Repository",
    "--env", "DISPLAY=:0",
    "--env", "WAYLAND_DISPLAY=wayland-0",
    "--env", "XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir",
    "--env", "PULSE_SERVER=/mnt/wslg/PulseServer",
    $imageName
)

# Display command (for debugging)
Write-Host "Running Docker container with command:"
Write-Host "docker $($dockerArgs -join ' ')"

# Run the docker command safely
Start-Process -NoNewWindow -FilePath "docker" -ArgumentList $dockerArgs -Wait


