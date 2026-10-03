"""Reproducible XOR, symmetry, activation, and three-class PyTorch experiments."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn


torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

INPUTS = torch.tensor(
    [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=torch.float32
)
BINARY_LABELS = torch.tensor([[0.0], [1.0], [1.0], [0.0]], dtype=torch.float32)
CLASS_LABELS = torch.tensor([0, 1, 1, 2], dtype=torch.long)
EXPECTED_BINARY = [0, 1, 1, 0]
EXPECTED_CLASSES = [0, 1, 1, 2]
TRAINING_STEPS = 6000
LEARNING_RATE = 0.03
SEED = 2


class BinaryXORNet(nn.Module):
    """2 inputs -> 2 nonlinear hidden units -> 1 binary logit."""

    def __init__(self, activation: str) -> None:
        super().__init__()
        self.hidden = nn.Linear(2, 2)
        self.output = nn.Linear(2, 1)
        self.activation_name = activation

    def forward(self, x: Tensor) -> Tensor:
        hidden = self.hidden(x)
        if self.activation_name == "sigmoid":
            hidden = torch.sigmoid(hidden)
        elif self.activation_name == "tanh":
            hidden = torch.tanh(hidden)
        elif self.activation_name == "relu":
            hidden = torch.relu(hidden)
        else:
            raise ValueError(f"Unknown hidden activation: {self.activation_name}")
        return self.output(hidden)  # Return logits for BCEWithLogitsLoss.


class ThreeClassNet(nn.Module):
    """2 inputs -> 2 sigmoid hidden units -> 3 class logits."""

    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(2, 2)
        self.output = nn.Linear(2, 3)

    def forward(self, x: Tensor) -> Tensor:
        return self.output(torch.sigmoid(self.hidden(x)))


@dataclass
class BinaryRun:
    model: BinaryXORNet
    initial_loss: float
    final_loss: float
    probabilities: list[float]
    labels: list[int]
    early_gradient: Tensor


def train_binary(activation: str, *, seed: int = SEED, zero_init: bool = False) -> BinaryRun:
    torch.manual_seed(seed)
    model = BinaryXORNet(activation)
    if zero_init:
        # Zeroing biases too gives both hidden units exactly the same starting state.
        for parameter in model.parameters():
            nn.init.zeros_(parameter)

    loss_function = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    with torch.no_grad():
        initial_loss = loss_function(model(INPUTS), BINARY_LABELS).item()

    early_gradient: Tensor | None = None
    for step in range(TRAINING_STEPS):
        optimizer.zero_grad(set_to_none=True)
        logits = model(INPUTS)
        loss = loss_function(logits, BINARY_LABELS)
        loss.backward()
        if step == 0:
            assert model.hidden.weight.grad is not None
            early_gradient = model.hidden.weight.grad.detach().clone()
        optimizer.step()

    with torch.no_grad():
        probabilities = torch.sigmoid(model(INPUTS)).flatten()
        labels = (probabilities >= 0.5).to(torch.int64)
        final_loss = loss_function(model(INPUTS), BINARY_LABELS).item()

    assert early_gradient is not None
    return BinaryRun(
        model=model,
        initial_loss=initial_loss,
        final_loss=final_loss,
        probabilities=[value.item() for value in probabilities],
        labels=labels.tolist(),
        early_gradient=early_gradient,
    )


def train_three_class() -> tuple[ThreeClassNet, float, Tensor]:
    torch.manual_seed(SEED)
    model = ThreeClassNet()
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    for _ in range(10_000):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(model(INPUTS), CLASS_LABELS)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        logits = model(INPUTS)
        probabilities = torch.softmax(logits, dim=1)
        final_loss = loss_function(logits, CLASS_LABELS).item()
    return model, final_loss, probabilities


def run_symmetry_experiment() -> tuple[dict[int, float], Tensor, float]:
    torch.manual_seed(SEED)
    model = BinaryXORNet("sigmoid")
    for parameter in model.parameters():
        nn.init.zeros_(parameter)
    loss_function = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    snapshots: dict[int, float] = {}
    initial_rows = model.hidden.weight.detach().clone()
    for step in range(101):
        if step in (0, 1, 10, 100):
            rows = model.hidden.weight.detach()
            snapshots[step] = torch.max(torch.abs(rows[0] - rows[1])).item()
        if step == 100:
            break
        optimizer.zero_grad(set_to_none=True)
        loss = loss_function(model(INPUTS), BINARY_LABELS)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        final_loss = loss_function(model(INPUTS), BINARY_LABELS).item()
    return snapshots, initial_rows, final_loss


def run_three_class_gradient_check(
    model: ThreeClassNet,
) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    logits = model(INPUTS).detach().requires_grad_(True)
    loss = nn.CrossEntropyLoss()(logits, CLASS_LABELS)
    loss.backward()
    assert logits.grad is not None
    probabilities = torch.softmax(logits.detach(), dim=1)
    one_hot = torch.nn.functional.one_hot(CLASS_LABELS, num_classes=3).float()
    expected_mean_gradient = (probabilities - one_hot) / len(INPUTS)
    assert torch.allclose(logits.grad, expected_mean_gradient, atol=1e-6)
    shifted = torch.softmax(logits.detach() + 100.0, dim=1)
    assert torch.allclose(shifted, probabilities, atol=1e-6)
    return probabilities, one_hot, logits.grad.detach(), shifted


def main() -> None:
    print("PyTorch version:", torch.__version__)
    print("Device: CPU; seed:", SEED)
    print("Input order: (0,0), (0,1), (1,0), (1,1)")
    print("Binary labels:", EXPECTED_BINARY)

    baseline = train_binary("sigmoid")
    print("\nBinary XOR baseline (2-2-1, sigmoid hidden, BCEWithLogitsLoss)")
    print(f"Initial loss: {baseline.initial_loss:.8f}")
    print(f"Final loss:   {baseline.final_loss:.8f}")
    print("Probabilities:", [round(x, 6) for x in baseline.probabilities])
    print("Predicted labels:", baseline.labels)
    print("Early first-layer weight gradient:\n", baseline.early_gradient)
    print(f"Early first-layer gradient L2 norm: {baseline.early_gradient.norm().item():.8f}")
    assert baseline.labels == EXPECTED_BINARY
    assert baseline.final_loss < baseline.initial_loss
    assert baseline.early_gradient.norm().item() > 0
    print("Basic learning checks: PASS")

    print("\nZero-initialization symmetry experiment (all parameters start at zero)")
    differences, initial_rows, zero_loss = run_symmetry_experiment()
    print("Initial hidden weight rows:\n", initial_rows)
    print("Maximum difference between hidden weight rows by step:", differences)
    print(f"Loss after 100 steps: {zero_loss:.8f}")
    assert all(value == 0.0 for value in differences.values())
    print("Hidden-unit symmetry check: PASS")

    print("\nActivation experiment (same seed, data, architecture, optimizer, and steps)")
    activation_runs: dict[str, BinaryRun] = {}
    for activation in ("sigmoid", "tanh", "relu"):
        result = train_binary(activation)
        activation_runs[activation] = result
        correct = result.labels == EXPECTED_BINARY
        print(
            f"{activation:7s} final_loss={result.final_loss:.8f} "
            f"correct_4_of_4={correct} "
            f"early_grad_norm={result.early_gradient.norm().item():.8f} "
            f"probabilities={[round(x, 6) for x in result.probabilities]}"
        )
        assert correct

    print("\nThree-class extension (2-2-3 logits, CrossEntropyLoss)")
    class_model, class_loss, class_probabilities = train_three_class()
    predicted_classes = class_probabilities.argmax(dim=1).tolist()
    row_sums = class_probabilities.sum(dim=1)
    print("Final output weight shape:", tuple(class_model.output.weight.shape))
    print("Logit shape:", (len(INPUTS), 3))
    print(f"Final loss: {class_loss:.8f}")
    print("Probabilities for (00, 01, 10, 11):")
    for inputs, probabilities in zip(INPUTS.to(torch.int64).tolist(), class_probabilities.tolist()):
        print(f"  {tuple(inputs)} -> {[round(x, 6) for x in probabilities]}")
    print("Probability row sums:", [round(x.item(), 8) for x in row_sums])
    print("Predicted classes:", predicted_classes)
    assert tuple(class_model.output.weight.shape) == (3, 2)
    assert predicted_classes == EXPECTED_CLASSES
    assert torch.allclose(row_sums, torch.ones_like(row_sums), atol=1e-6)

    probabilities, one_hot, observed_gradient, shifted = run_three_class_gradient_check(class_model)
    print("For the first example, softmax p:", probabilities[0].tolist())
    print("One-hot y:", one_hot[0].tolist())
    print("Observed mean-loss logit gradient:", observed_gradient[0].tolist())
    print("Expected (p-y)/4:", ((probabilities - one_hot) / len(INPUTS))[0].tolist())
    print("Softmax after adding 100 to every logit:", shifted[0].tolist())
    print("Three-class checks (accuracy, sum-to-one, p-y gradient, shift invariance): PASS")


if __name__ == "__main__":
    main()
