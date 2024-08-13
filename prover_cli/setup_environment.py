import subprocess

def setup_environment():
    commands = [
        'mkdir -p /tmp/proofs',
        'mkdir -p /tmp/witnesses'
    ]

    for command in commands:
        print(f"Executing setup command: {command}")
        try:
            result = subprocess.run(['sh', '-c', command], capture_output=True, text=True)
            if result.stderr:
                print(f"Setup command error: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Setup command failed with error: {e.stderr}")
