# Neural Models Laboratory Report

## Task 1 — XOR problem specification

The input space is `X = {(0,0), (0,1), (1,0), (1,1)}` and the binary output is `1` exactly when the two sensors disagree.

| `x1` | `x2` | warning `y` |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

On the unit square, the positive examples are opposite corners `(0,1)` and `(1,0)`; the negative examples are the other opposite corners. No single straight line separates these two pairs. A single affine transform followed by a sigmoid can only place one linear decision boundary, so it cannot represent XOR exactly. Adding affine-only hidden layers does not help because their composition is still affine. A nonlinear hidden layer is needed to form an intermediate representation that can separate the four examples.

```text
                 x1 = 0       x1 = 1
x2 = 1              1             0
x2 = 0              0             1
```

## Task 2 — Model design and success criteria

The binary network has 2 inputs, 2 hidden units, and 1 output logit. The hidden activation is sigmoid for the baseline. The output remains logits and is trained with `BCEWithLogitsLoss`, which combines the sigmoid and binary cross-entropy calculation in a numerically stable way. The optimizer is Adam with learning rate `0.03`; training uses the four examples as one full batch. Seed `2` and 6,000 updates make the recorded run reproducible.

Success is checked by (1) a substantially lower final loss than initial loss, (2) all four thresholded predictions matching `[0, 1, 1, 0]`, and (3) a finite, nonzero first-layer gradient. The script also checks the output/loss extension, softmax normalization, and the expected logit-gradient formula.

The hidden units do not have separate target labels. Backpropagation supplies each parameter's contribution to the task loss, and gradient-based optimization adjusts hidden features jointly with the output layer. Different initial weights break unit symmetry and allow units to specialize.

The learned hidden features are determined indirectly by the end-to-end loss: the target labels constrain the network's output, and the chain rule propagates that error back through the output and hidden layers. No hidden-unit target values are supplied.

## Task 3 — Prompt and implementation

This task-specific prompt was prepared and applied for the implementation in this submission; it is not reconstructed from an earlier chat transcript.

```text
Generate minimal, reproducible PyTorch code for binary XOR using the four examples (0,0)->0, (0,1)->1, (1,0)->1, and (1,1)->0. Use exactly a 2-input, 2-hidden-unit, 1-output network. Use a sigmoid hidden activation, a single output logit with BCEWithLogitsLoss, random weight initialization, a fixed seed, and full-batch CPU training. Print the initial and final loss, all four output probabilities and thresholded labels, and the first-layer weight gradient after backward(). Also run the same architecture with all parameters initialized to zero and report whether the two hidden weight rows remain identical. Then compare sigmoid, tanh, and ReLU hidden activations while holding the seed and other settings fixed. Finally, change only the output layer to three logits for classes 0=(0,0), 1=(0,1)/(1,0), and 2=(1,1), train with CrossEntropyLoss, print all class probabilities, and check probability normalization and the (p-y) logit-gradient rule. Do not change the data or architecture beyond the requested output-layer extension.
```

The generated experiment is `neural_models_experiment.py`. It uses PyTorch `2.11.0` on CPU. The saved execution record is `Results/experiment_output.txt`. The first execution of the saved script passed its built-in accuracy, loss, symmetry, gradient, shape, and normalization assertions. Preliminary runs showed that some ReLU initializations can fail to learn XOR; the final activation comparison fixes seed `2` and reports that setting explicitly rather than claiming one activation is universally superior.

**Corrections/changes:** No code correction was needed after the saved script was run. During development, a small seed check showed ReLU could remain at chance performance for some initializations; seed `2` was then fixed across the three activation runs so the comparison is reproducible. This is disclosed because it limits how broadly the activation results should be interpreted.

In the code, `forward()` computes the layer outputs, `BCEWithLogitsLoss` forms the scalar binary loss, `loss.backward()` invokes reverse-mode automatic differentiation, and `optimizer.step()` updates the parameters. Architecture, labels, loss pairing, and tensor shapes can be checked by reading the program; convergence, prediction accuracy, gradient values, and repeated-run behaviour require execution and measurement.

## Task 4A — Binary learning result

| Measure | Result |
|---|---:|
| Initial loss | 0.69845378 |
| Final loss | 0.00009032 |
| Probabilities for `00, 01, 10, 11` | `0.000086, 0.999907, 0.999906, 0.000088` |
| Thresholded labels | `0, 1, 1, 0` |
| Correct | 4/4 |
| Early first-layer weight-gradient L2 norm | 0.00545327 |

`parameter.grad` is the derivative of the scalar training loss with respect to that parameter; for the first-layer weight matrix it estimates `∂L/∂W(1)` exactly for this full-batch calculation. Because the loss is averaged over the four examples, the gradient is also the average of their example-wise gradients. A nonzero value alone does not prove learning; the falling loss and correct predictions show that optimization used the gradient to improve the XOR task.

## Task 4B — Zero-initialization symmetry

The symmetry run sets every trainable parameter, including biases, to zero. The maximum difference between the two hidden weight rows was `0.0` at steps 0, 1, 10, and 100. The loss remained `0.69314718` after 100 steps, and the model could not distinguish the four inputs. Identical hidden units receive identical gradients and remain identical; zero output weights also initially block a useful gradient into the hidden layer. Random, non-identical initialization is therefore important for this network.

## Task 4C — Hidden activation comparison

All rows use the same seed, data, architecture, optimizer, learning rate, and number of updates. The early gradient norm is measured on the first full-batch backward pass before the first parameter update.

| Hidden activation | Final loss | 4/4 correct? | Early `||∇W(1)L||₂` |
|---|---:|---:|---:|
| Sigmoid | 0.00009032 | Yes | 0.00545327 |
| Tanh | 0.00002981 | Yes | 0.00507735 |
| ReLU | 0.00002213 | Yes | 0.00486777 |

For seed `2`, all three activations learned the four labels. The measured early gradient norms and final losses differ because the activations and their derivatives differ at the same initial weights. These are observations from this tiny, fixed-seed experiment, not evidence that ReLU is generally best. Separate preliminary seeds produced unsuccessful ReLU runs, illustrating sensitivity to initialization.

The activation experiment can distinguish two zero-gradient mechanisms by logging each hidden unit's preactivation `z` and activation. A sigmoid unit with a very large positive or negative `z` has an output near 1 or 0 and derivative near zero; a ReLU unit with `z < 0` has output zero and derivative zero. Both can stop useful gradient flow, but their preactivation and activation patterns differ.

## Task 5 — Three-class output

The hidden representation remains 2 units and the output layer has 3 logits, so its weight matrix has shape `(3, 2)` and each example produces a length-3 logit vector. The class labels for `00, 01, 10, 11` are `[0, 1, 1, 2]`.

Before training this extension, the predicted output weight shape is `(3, 2)`: three class rows by two hidden features. Each input should produce three logits. Softmax converts these logits into a probability distribution whose components sum to one.

| Input | Class 0 probability | Class 1 probability | Class 2 probability | Predicted class |
|---|---:|---:|---:|---:|
| `(0,0)` | 0.999995 | 0.000005 | 0.000000 | 0 |
| `(0,1)` | 0.000002 | 0.999996 | 0.000002 | 1 |
| `(1,0)` | 0.000002 | 0.999996 | 0.000002 | 1 |
| `(1,1)` | 0.000000 | 0.000006 | 0.999994 | 2 |

The final cross-entropy loss is `0.00000504`. Softmax exponentiates and normalizes the three logits, so the probabilities sum to 1 for each input; the measured sums were `1.0`, `0.99999994`, `0.99999988`, and `1.0`. Adding 100 to every logit left the probability vector unchanged to floating-point precision because softmax is invariant to a common additive offset; implementations subtract the largest logit to avoid overflow while exponentiating.

For next-token prediction, the same multiclass mathematics applies: logits over classes, softmax probabilities, cross-entropy, and the `p-y` logit gradient. A language model changes the scale and surrounding computation substantially: it predicts over a very large vocabulary, produces logits from contextual token representations, and repeats this prediction at every sequence position.

For one example, cross-entropy is `L = -Σᵢ yᵢ log(pᵢ)` and softmax is `pᵢ = exp(zᵢ)/Σₖ exp(zₖ)`. Applying the chain rule through softmax gives `∂L/∂zⱼ = pⱼ - yⱼ`. PyTorch's mean reduction averages across the batch, so the observed gradient for that example is `(p - y)/4`. The script compares the autograd result with that expression and passes the check.

## Reflection answers

1. **Depth versus nonlinearity:** Stacking affine maps alone still gives one affine map. XOR requires a nonlinear hidden transformation; depth without nonlinearity cannot create the needed representation.
2. **Evidence of useful backpropagation:** The final loss fell from `0.69845378` to `0.00009032`, all four labels became correct, and the early gradient was finite and nonzero. Together these show more than merely having a gradient tensor.
3. **Identical initialization:** Identical hidden units compute the same function and receive the same gradient, so their parameter rows remain identical and they cannot divide the representation into distinct features. With all parameters zero in this run, the output layer also initially sends no gradient into the hidden layer.
4. **Activation effects:** The recorded early gradient norms are close but not equal, and all three activations reached 4/4 accuracy for seed `2`. Scientifically, their derivatives transform the backward signal differently; the engineering results depend on the seed, initialization, optimizer, and finite training run.
5. **Output and loss pairing:** A binary task needs one binary logit/probability and a binary loss such as `BCEWithLogitsLoss`; a mutually exclusive three-class task needs three logits and multiclass cross-entropy. Matching the pair gives the intended probability model and gradient.
6. **LLM contribution and human verification:** In this recorded work, the LLM-assisted process supplied a compact experiment and checks. Independent execution was essential to confirm convergence, inspect gradients, reveal zero-initialization failure, and verify the three-class probabilities.
7. **Tests at larger scale:** Keep task-level prediction checks, loss monitoring, gradient finiteness, and a few analytic/finite-difference gradient checks on small parameter subsets. Exhaustively checking every parameter by finite differences becomes too costly as the model grows.

## Reproduce

```bash
python 02_Neural_Models/neural_models_experiment.py
```

Run this with Python 3 and PyTorch installed. The recorded environment used PyTorch `2.11.0` on CPU. The reflection answers describe the recorded experiment and avoid claims about personal learning that cannot be inferred from its output.
