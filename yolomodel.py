from ultralytics import YOLO

def train_yolov8_model():
    # Load a pre-trained YOLOv8 model
    model = YOLO('yolov8n.pt')  # Load the YOLOv8 nano model. You can change this to other versions like yolov8s.pt, yolov8m.pt, etc.

    # Train the model on your custom dataset
    results = model.train(
        data='/Users/chiru/PycharmProjects/PPEproject/media/data.yaml',  # Path to your dataset configuration file
        epochs=300,                         # Number of epochs to train for
        imgsz=640,                         # Image size
    )
    # Save the trained model
    model.save('best-model.pt')

    return model

if __name__ == "__main__":
    # Train the model
    model = train_yolov8_model()
