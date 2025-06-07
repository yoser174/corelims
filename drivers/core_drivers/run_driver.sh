python3 -m run_driver "$@"
if [ $? -ne 0 ]; then
    echo "Error: Failed to run the driver."
    exit 1
fi
echo "Driver executed successfully."