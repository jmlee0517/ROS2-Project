import csv
import math
import random
from pathlib import Path

from my_py_pkg.kinematics import forward_kinematics


# Robot geometry (metres)
L1 = 0.1375
L2 = 0.120
L3 = 0.075
SHOULDER_HEIGHT = 0.110

# Joint limits (radians)
BASE_MIN = -1.5708
BASE_MAX = 1.5708

SHOULDER_MIN = -0.7854
SHOULDER_MAX = 1.3090

ELBOW_MIN = 0.05
ELBOW_MAX = 2.0944

WRIST_MIN = -1.5708
WRIST_MAX = 1.5708

# Fixed end-effector orientation
TARGET_PITCH = math.pi

# Dataset settings
NUM_SAMPLES = 50_000
RANDOM_SEED = 42 #use the same seed for reproducibility when comparing datasets.

# Save dataset in the workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = WORKSPACE_ROOT / "datasets"
OUTPUT_FILE = OUTPUT_DIR / "ik_dataset.csv"


def generate_sample():
    """
    Generate one valid joint configuration and its end-effector position.

    Uses the positive elbow branch and fixed end-effector pitch.
    Returns a dictionary containing XYZ and joint angles.
    """

    # Randomly sample the first three joints (we use continuous uniform distributions)
    theta0 = random.uniform(BASE_MIN, BASE_MAX)
    theta1 = random.uniform(SHOULDER_MIN, SHOULDER_MAX)
    theta2 = random.uniform(ELBOW_MIN, ELBOW_MAX)

    # Calculate wrist angle to maintain the desired pitch
    theta3 = TARGET_PITCH - theta1 - theta2

    # Reject configurations outside the wrist joint limits
    if not WRIST_MIN <= theta3 <= WRIST_MAX:
        return None

    joint_angles = [theta0, theta1, theta2, theta3]

    # Calculate end-effector position using 4-DOF forward kinematics
    x, y, z = forward_kinematics(joint_angles)

    return {
        "x": x,
        "y": y,
        "z": z,
        "base_rotation": theta0,
        "shoulder": theta1,
        "elbow": theta2,
        "wrist": theta3,
        "end_effector_pitch_rad": TARGET_PITCH,
    }


def main():
    random.seed(RANDOM_SEED)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    samples = []
    attempts = 0
    max_attempts = NUM_SAMPLES * 100

    print("Generating inverse kinematics dataset...")
    print(f"Target samples: {NUM_SAMPLES}")

    next_progress = 5000

    while len(samples) < NUM_SAMPLES and attempts < max_attempts:
        attempts += 1

        sample = generate_sample()

        if sample is not None:
            samples.append(sample)

        if len(samples) >= next_progress:
            print(f"Generated {len(samples)} / {NUM_SAMPLES} samples")
            next_progress += 5000

    if len(samples) < NUM_SAMPLES:
        raise RuntimeError(
            f"Could only generate {len(samples)} samples "
            f"after {attempts} attempts."
        )

    fieldnames = [
        "sample_id",
        "x",
        "y",
        "z",
        "base_rotation",
        "shoulder",
        "elbow",
        "wrist",
        "end_effector_pitch_rad",
    ]

    with OUTPUT_FILE.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for sample_id, sample in enumerate(samples):
            writer.writerow({
                "sample_id": sample_id,
                **sample,
            })

    print("\nDataset generation completed.")
    print(f"Accepted samples: {len(samples)}")
    print(f"Total attempts: {attempts}")
    print(f"Acceptance rate: {len(samples) / attempts * 100:.2f}%")
    print(f"Dataset saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()