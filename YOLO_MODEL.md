# YOLO Model — Training, Location and Replacement

This document covers everything you need to know about the YOLOv8 detection model used by nuts_vision: where it lives in the project, how to train a new one, and how to swap in a different model.

---

## Model location in the project

| Path | Description |
|------|-------------|
| `runs/detect/component_detector/weights/best.pt` | Default trained model (created after training) |
| `runs/detect/component_detector/weights/last.pt` | Last checkpoint from the most recent training run |
| `data.yaml` | YOLO dataset configuration (class names, dataset paths) |
| `src/train.py` | Training script |

The web interface (`app.py`) and the pipeline (`src/pipeline.py`) both look for the model at `runs/detect/component_detector/weights/best.pt` by default. You can override this path at any time (see [Replacing the model](#replacing-the-model)).

---

## Dataset

The default model is trained on **CompDetect v3** from Roboflow:

- **Images**: 583 annotated PCB photos
- **Classes** (16): IC, LED, battery, buzzer, capacitor, clock, connector, diode, display, fuse, inductor, potentiometer, relay, resistor, switch, transistor
- **Format**: YOLOv8 (YOLO annotation format)
- **License**: CC BY 4.0
- **Roboflow URL**: https://app.roboflow.com/peanuts-q9amc/compdetect-f6vw8/3

The `data.yaml` file at the repository root points to the dataset directories:

```yaml
train: ../train/images
val:   ../valid/images
test:  ../test/images

nc: 16
names: [IC, LED, battery, buzzer, capacitor, clock, connector, diode,
        display, fuse, inductor, potentiometer, relay, resistor, switch, transistor]
```

Download the dataset from Roboflow and extract it so that `train/`, `valid/`, and `test/` sit one level above the repository root (or update the paths in `data.yaml` to match your layout).

---

## Training a model from scratch

### 1. Prepare the dataset

Download the CompDetect v3 dataset in **YOLOv8 format** from the Roboflow URL above, or use your own annotated dataset in the same format. Make sure `data.yaml` points to the correct directories.

### 2. Run the training script

```bash
python src/train.py \
  --data data.yaml \
  --model-size n \
  --epochs 100 \
  --batch 16 \
  --imgsz 640 \
  --device 0        # GPU id, or 'cpu'
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--data` | `data.yaml` | Path to the YOLO dataset config file |
| `--model-size` | `n` | YOLOv8 variant: `n` nano · `s` small · `m` medium · `l` large · `x` xlarge |
| `--epochs` | `100` | Number of training epochs |
| `--batch` | `16` | Batch size (reduce if you run out of GPU memory) |
| `--imgsz` | `640` | Input image size (pixels) |
| `--name` | `component_detector` | Sub-folder name under `runs/detect/` |
| `--device` | `0` | CUDA device id or `cpu` |

After training completes, the best weights are saved automatically to:

```
runs/detect/component_detector/weights/best.pt
```

This path is the default expected by the rest of the application — no further configuration is needed.

### 3. Training tips

- **GPU strongly recommended.** Training 100 epochs on a CPU takes many hours; on a mid-range GPU it takes 30–90 minutes.
- **Model size trade-off**: `n` (nano) is fastest and smallest; `x` (xlarge) is most accurate but requires more memory and time.
- **Early stopping**: The script sets a patience of 50 epochs, so training will stop automatically if validation metrics stop improving.
- **Checkpoints**: A checkpoint is saved every 10 epochs, in addition to `best.pt` and `last.pt`.

---

## Replacing the model

You can point the application to any compatible `.pt` file (a YOLOv8 model trained for the same 16 classes, or adapted to your own classes).

### In the web interface

On the **Upload & Process** page, the *Model Path* input field lets you enter any path to a `.pt` file before starting a batch.

### On the command line

```bash
python src/pipeline.py \
  --model /path/to/your/custom_model.pt \
  --image board.jpg
```

### Permanently changing the default

Edit the two lines in `app.py` that define `default_model_path`:

```python
# app.py — Upload & Process page
default_model_path = "runs/detect/component_detector/weights/best.pt"
```

Replace the string with your preferred path. The Job Viewer and About pages also reference `runs/detect/component_detector/weights/best.pt` — update them in the same way if needed.

---

## Re-training on a custom dataset

If you have your own set of annotated PCB images, follow these steps:

1. **Annotate** your images in YOLO format (Roboflow is a convenient tool for this).
2. **Create a `data.yaml`** that lists your dataset paths and class names (use the existing `data.yaml` as a template).
3. **Run training** with `--data your_data.yaml`.
4. The resulting `best.pt` will reflect your custom classes. Update the class names list in the application if they differ from the default 16.

---

## Verifying a trained model

After training, you can quickly test the model from the command line:

```bash
python src/detect.py \
  --model runs/detect/component_detector/weights/best.pt \
  --image path/to/test_board.jpg \
  --conf 0.25
```

Or launch the web interface and use the **Upload & Process** page to run the full pipeline on a test image.
