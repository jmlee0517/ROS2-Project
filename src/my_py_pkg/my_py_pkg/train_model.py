import csv
import math
import random
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from my_py_pkg.kinematics import forward_kinematics


# --------------------------------------------------
# Reproducibility
# --------------------------------------------------

SEED = 42

random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# --------------------------------------------------
# Paths and training configuration
# --------------------------------------------------

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = WORKSPACE_ROOT / "datasets" / "ik_dataset.csv"
MODEL_DIR = WORKSPACE_ROOT / "models"
MODEL_PATH = MODEL_DIR / "pytorch_ik_model.pth"

BATCH_SIZE = 128
LEARNING_RATE = 0.001
MAX_EPOCHS = 200
PATIENCE = 20

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# --------------------------------------------------
# Neural network
# --------------------------------------------------

class IKNetwork(nn.Module):

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(3, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 4)
        )

    def forward(self, x):
        return self.network(x)


# --------------------------------------------------
# Dataset loading
# --------------------------------------------------

def load_dataset():

    inputs = []
    targets = []

    with DATASET_PATH.open("r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:

            xyz = [
                float(row["x"]),
                float(row["y"]),
                float(row["z"])
            ]

            joint_angles = [
                float(row["base_rotation"]),
                float(row["shoulder"]),
                float(row["elbow"]),
                float(row["wrist"])
            ]

            inputs.append(xyz)
            targets.append(joint_angles)

    X = torch.tensor(inputs, dtype=torch.float32)
    y = torch.tensor(targets, dtype=torch.float32)

    return X, y


# --------------------------------------------------
# Dataset splitting and normalization
# --------------------------------------------------

def prepare_datasets(X, y):

    total_samples = len(X)

    generator = torch.Generator().manual_seed(SEED)
    indices = torch.randperm(total_samples, generator=generator)

    train_end = int(total_samples * 0.70)
    validation_end = int(total_samples * 0.85)

    train_indices = indices[:train_end]
    validation_indices = indices[train_end:validation_end]
    test_indices = indices[validation_end:]

    X_train = X[train_indices]
    y_train = y[train_indices]

    X_validation = X[validation_indices]
    y_validation = y[validation_indices]

    # Preserve original test coordinates in metres.
    X_test_raw = X[test_indices].clone()
    y_test = y[test_indices]

    # Calculate normalization statistics using training data only.
    X_mean = X_train.mean(dim=0)
    X_std = X_train.std(dim=0)
    X_std = torch.clamp(X_std, min=1e-8)

    # Normalize model inputs.
    X_train = (X_train - X_mean) / X_std
    X_validation = (X_validation - X_mean) / X_std
    X_test_normalized = (X_test_raw - X_mean) / X_std

    train_dataset = TensorDataset(X_train, y_train)
    validation_dataset = TensorDataset(X_validation, y_validation)
    test_dataset = TensorDataset(X_test_normalized, y_test)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=torch.Generator().manual_seed(SEED)
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    normalization = {
        "mean": X_mean,
        "std": X_std
    }

    return (
        train_loader,
        validation_loader,
        test_loader,
        normalization,
        X_test_raw,
        y_test
    )

# --------------------------------------------------
# Training and validation
# --------------------------------------------------

def calculate_loss(model, data_loader, criterion):

    model.eval()
    total_loss = 0.0

    with torch.no_grad():

        for inputs, targets in data_loader:

            inputs = inputs.to(DEVICE)
            targets = targets.to(DEVICE)

            predictions = model(inputs)

            loss = criterion(predictions, targets)

            total_loss += loss.item() * len(inputs)

    return total_loss / len(data_loader.dataset)


def train_model(
    model,
    train_loader,
    validation_loader,
    normalization
):

    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    best_validation_loss = float("inf")
    epochs_without_improvement = 0

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    for epoch in range(MAX_EPOCHS):

        model.train()
        total_training_loss = 0.0

        for inputs, targets in train_loader:

            inputs = inputs.to(DEVICE)
            targets = targets.to(DEVICE)

            # Reset gradients from the previous batch.
            optimizer.zero_grad()

            # Forward pass.
            predictions = model(inputs)

            # Calculate loss.
            loss = criterion(predictions, targets)

            # Backpropagation.
            loss.backward()

            # Update network weights.
            optimizer.step()

            total_training_loss += loss.item() * len(inputs)

        training_loss = (
            total_training_loss / len(train_loader.dataset)
        )

        validation_loss = calculate_loss(
            model,
            validation_loader,
            criterion
        )

        print(
            f"Epoch [{epoch + 1:03d}/{MAX_EPOCHS}] "
            f"Training Loss: {training_loss:.8f} "
            f"Validation Loss: {validation_loss:.8f}"
        )

        # Save the model whenever validation improves.
        if validation_loss < best_validation_loss:

            best_validation_loss = validation_loss
            epochs_without_improvement = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "input_mean": normalization["mean"],
                    "input_std": normalization["std"],
                    "best_validation_loss": best_validation_loss,
                    "epoch": epoch + 1,
                },
                MODEL_PATH
            )

        else:
            epochs_without_improvement += 1

        # Early stopping.
        if epochs_without_improvement >= PATIENCE:

            print(
                f"\nEarly stopping at epoch {epoch + 1}."
            )
            break

    print("\nTraining completed.")
    print(f"Best validation loss: {best_validation_loss:.8f}")
    print(f"Best model saved to: {MODEL_PATH}")


# --------------------------------------------------
# Test evaluation
# --------------------------------------------------

def evaluate_model(model, test_loader, X_test, y_test, normalization):

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_predictions = []

    with torch.no_grad():

        for inputs, _ in test_loader:

            inputs = inputs.to(DEVICE)
            predictions = model(inputs)

            all_predictions.append(predictions.cpu())

    predictions = torch.cat(all_predictions, dim=0)

    # Joint-angle errors.
    joint_errors = torch.abs(predictions - y_test)

    joint_names = [
        "Base rotation",
        "Shoulder",
        "Elbow",
        "Wrist"
    ]

    print("\n--- Joint-angle evaluation ---")

    for i, name in enumerate(joint_names):

        mean_error = joint_errors[:, i].mean().item()

        print(
            f"{name}: mean absolute error = "
            f"{mean_error:.6f} rad"
        )

    # Reconstruct Cartesian positions using FK.
    cartesian_errors = []

    for predicted_angles, target_xyz in zip(predictions, X_test):

        predicted_xyz = forward_kinematics(
            predicted_angles.tolist()
        )

        target_xyz = target_xyz.tolist()

        error = math.sqrt(
            sum(
                (predicted_xyz[i] - target_xyz[i]) ** 2
                for i in range(3)
            )
        )

        cartesian_errors.append(error)

    errors = torch.tensor(cartesian_errors, dtype=torch.float64)

    mean_error = errors.mean().item()
    median_error = errors.median().item()
    max_error = errors.max().item()
    rmse = torch.sqrt(torch.mean(errors ** 2)).item()

    # Positioning success rate using the 2 mm tolerance.
    tolerance = 0.002  # metres

    successful_predictions = (errors <= tolerance).sum().item()
    total_predictions = len(errors)

    success_rate = (
        successful_predictions / total_predictions
    ) * 100

    print("\n--- Positioning tolerance evaluation ---")
    print(f"Tolerance: {tolerance * 1000:.1f} mm")
    print(f"Successful predictions: {successful_predictions}/{total_predictions}")
    print(f"Success rate: {success_rate:.2f}%")

    print(
        f"95th percentile error: "
        f"{torch.quantile(errors, 0.95).item() * 1000:.6f} mm"
    )

    print("\n--- Cartesian positioning evaluation ---")
    print(f"Mean error:   {mean_error * 1000:.6f} mm")
    print(f"Median error: {median_error * 1000:.6f} mm")
    print(f"Maximum error:{max_error * 1000:.6f} mm")
    print(f"RMSE:         {rmse * 1000:.6f} mm")

    # Single-sample inference timing (model forward pass only).
    sample = (
        (X_test[0:1].to(DEVICE) - normalization["mean"].to(DEVICE))
        / normalization["std"].to(DEVICE)
    )

    with torch.no_grad():
        for _ in range(20):
            model(sample)

        start = time.perf_counter()

        for _ in range(1000):
            model(sample)

        elapsed = time.perf_counter() - start

    average_inference_ms = elapsed / 1000 * 1000

    print("\n--- Inference timing ---")
    print(
        f"Average single-sample inference: "
        f"{average_inference_ms:.6f} ms"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------
'''
#Training from the beginning
def main():

    print(f"Using device: {DEVICE}")

    print("\nLoading dataset...")
    X, y = load_dataset()

    print(f"Loaded {len(X)} samples.")

    print("\nSplitting and normalizing dataset...")

    (
        train_loader,
        validation_loader,
        test_loader,
        normalization,
        X_test,
        y_test
    ) = prepare_datasets(X, y)

    print(f"Training samples:   {len(train_loader.dataset)}")
    print(f"Validation samples: {len(validation_loader.dataset)}")
    print(f"Test samples:       {len(test_loader.dataset)}")

    model = IKNetwork().to(DEVICE)

    print("\nStarting training...")

    train_model(
        model,
        train_loader,
        validation_loader,
        normalization
    )

    print("\nEvaluating best model...")

    evaluate_model(
        model,
        test_loader,
        X_test,
        y_test,
        normalization
    )


if __name__ == "__main__":
    main()
'''

#Use the pretrained model to evaluate the test dataset
def main():

    print(f"Using device: {DEVICE}")

    print("\nLoading dataset...")
    X, y = load_dataset()

    print(f"Loaded {len(X)} samples.")

    (
        train_loader,
        validation_loader,
        test_loader,
        normalization,
        X_test,
        y_test
    ) = prepare_datasets(X, y)

    print("\nLoading existing trained model...")

    model = IKNetwork().to(DEVICE)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    print(f"Best training epoch: {checkpoint['epoch']}")
    print(
        f"Best validation loss: "
        f"{checkpoint['best_validation_loss']:.8f}"
    )

    print("\nEvaluating on test dataset...")

    evaluate_model(
        model,
        test_loader,
        X_test,
        y_test,
        normalization
    )


if __name__ == "__main__":
    main()
